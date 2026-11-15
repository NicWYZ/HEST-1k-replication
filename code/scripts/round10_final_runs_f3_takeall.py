"""Round 10, track final-runs, F3.3 (v): the probe and take-all design (plan, section 5d.3 (v)).

Modes
  anchor_check <new_by_gene_csv_gz> <ref_by_gene_csv_gz> <ref_medians_csv> <task> <out_json>
      Compares a rerun of round9_probe_takeall.py (unchanged, generator default_rng(20261027)) with round 9's committed
      gene rows for the task, and the medians over genes at k = 1, n_L = 8 with takeall_medians.csv.
  run <config.json> <out_dir>
      A population is (task, encoder, scale, estimand) with F2's cluster values z_g, f_g over its G donors (genes with
      a non-finite value dropped), and the task's spot file for the probe. Per cell (k, n_L), k in {1, 2}, n_L in
      {6, 8, 12}, skipped when n_L - k < 4 or n_L >= G, R repetitions with one generator default_rng(crc32(
      'f3ta|<task>|<encoder>|<scale>|<estimand>|k<k>|nL<n>')). In each repetition a fresh probe takes o spots per
      donor without replacement and sets u_hat_g to their mean over genes and spots of the scale's outcome (round 9's
      probe); the k donors furthest from the median u_hat are taken with certainty (T), n_r = n_L - k more are drawn
      from the other G - k (R) without replacement, and a fresh simple random sample of n_L donors is drawn for D0.
        T0        round 9's estimator: (sum_T z + (G - k) mean_S z)/G, variance ((G-k)/G)^2 (1 - n_r/(G-k)) s^2_S / n_r
        T0_fix1   (sum_T z + (G - k)(Fbar_R + mean_S e))/G with e = z - f, variance as T0 with s^2_{e,S}
        D0        the labelled mean, (1 - n_L/G) s^2/n_L;  D0_fix1  mean_L e + Fbar_U, the same variance of e
      T0 and T0_fix1 are referred to t_{n_r - 1}, D0 and D0_fix1 to t_{n_L - 1}. The interval conditions on the probe;
      coverage is taken over a fresh probe in every repetition, so it is unconditional.
Writes takeall_summary.json first, then takeall_cells.csv (medians over genes, both gene scopes) and
takeall_genes.parquet.
"""
import json, os, sys, time, zlib
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from scipy import stats

ALPHA = 0.10
R9_TASKS = ("LUNG_XENIUM",)
METHODS = ("D0", "D0_fix1", "T0", "T0_fix1")
GSCHEMA = pa.schema([(k, pa.string()) for k in ("task", "encoder", "scale", "estimand", "gene")] +
                    [("G", pa.int64()), ("k", pa.int64()), ("n_L", pa.int64()), ("method", pa.string()), ("R", pa.int64())] +
                    [(k, pa.float64()) for k in ("theta", "coverage", "coverage_se", "mean_width", "median_width",
                                                 "bias", "emp_var", "ev_over_var")])


def anchor_check(new_p, ref_p, med_p, task, out_json):
    a = pd.read_csv(new_p); b = pd.read_csv(ref_p); b = b[b.task == task]
    k = ["task", "k", "n_L", "method", "gene"]
    m = a.merge(b, on=k, how="outer", suffixes=("", "_ref"), indicator=True)
    out = dict(rows_new=len(a), rows_ref=len(b), rows_both=int((m["_merge"] == "both").sum()))
    for c in ("coverage", "mean_width"):
        out[f"max_abs_{c}"] = float(np.abs(m[c] - m[c + "_ref"]).max())
    med = pd.read_csv(med_p); med = med[med.task == task]
    rows = []
    for (kk, nl, meth), x in a.groupby(["k", "n_L", "method"]):
        r = med[(med.k == kk) & (med.n_L == nl) & (med.method == meth)]
        rows.append(dict(k=int(kk), n_L=int(nl), method=meth, median_coverage=float(x.coverage.median()),
                         median_coverage_ref=float(r.median_coverage.iloc[0]) if len(r) else np.nan))
    md = pd.DataFrame(rows)
    md["d4"] = (md.median_coverage.round(4) - md.median_coverage_ref).abs()
    out["medians_max_abs_diff_4dp"] = float(md.d4.max())
    named = md[(md.k == 1) & (md.n_L == 8)].set_index("method")
    out["named"] = {mm: dict(median_coverage=float(named.loc[mm, "median_coverage"]),
                             median_coverage_ref=float(named.loc[mm, "median_coverage_ref"])) for mm in ("T0", "D0")}
    out["exact"] = bool(out["rows_both"] == len(a) == len(b) and out["max_abs_coverage"] == 0 and out["max_abs_mean_width"] == 0)
    json.dump(out, open(out_json, "w"), indent=1)
    md.to_csv(out_json.replace(".json", "_medians.csv"), index=False)
    print(json.dumps(out, indent=1))
    return 0 if out["exact"] else 1


def probe_values(path, y_prefix, donor_col, donors):
    """Per donor, the spot-level mean over genes of the outcome (the probe averages these over o spots)."""
    import pyarrow.parquet as pq_
    cols = [c for c in pq_.read_schema(path).names if c.startswith(y_prefix)]
    d = pd.read_parquet(path, columns=[donor_col] + cols)
    did = d[donor_col].astype(str).to_numpy()
    yb = d[cols].to_numpy(np.float64).mean(1)
    return [yb[did == g] for g in donors], len(cols)


def draw_probe(rng, spots, R, o):
    """(R, G) u_hat: per donor, o distinct spots per repetition (integers redrawn row-wise until distinct)."""
    U = np.empty((R, len(spots)))
    for j, s in enumerate(spots):
        N = len(s)
        if N < o:
            raise ValueError(f"donor {j} has {N} < {o} spots")
        I = rng.integers(0, N, size=(R, o))
        while True:
            Ss = np.sort(I, 1); bad = (np.diff(Ss, axis=1) == 0).any(1)
            if not bad.any():
                break
            I[bad] = rng.integers(0, N, size=(int(bad.sum()), o))
        U[:, j] = s[I].mean(1)
    return U


def run_cell(z, f, spots, k, nL, R, o, rng):
    G, ng = z.shape; e = z - f; Fb = f.mean(0)
    U = draw_probe(rng, spots, R, o)
    nr = nL - k; Nr = G - k
    th = {m: np.empty((R, ng)) for m in METHODS}; v = {m: np.empty((R, ng)) for m in METHODS}
    for r in range(R):
        u = U[r]; dev = np.abs(u - np.median(u)); C = np.argsort(-dev, kind="stable")[:k]
        rest = np.setdiff1d(np.arange(G), C)
        S = np.sort(rng.choice(rest, nr, replace=False))
        L = np.sort(rng.choice(G, nL, replace=False))
        zS, eS = z[S], e[S]
        th["T0"][r] = (z[C].sum(0) + Nr * zS.mean(0)) / G
        v["T0"][r] = (Nr / G) ** 2 * (1 - nr / Nr) * zS.var(0, ddof=1) / nr
        th["T0_fix1"][r] = (z[C].sum(0) + Nr * (f[rest].mean(0) + eS.mean(0))) / G
        v["T0_fix1"][r] = (Nr / G) ** 2 * (1 - nr / Nr) * eS.var(0, ddof=1) / nr
        th["D0"][r] = z[L].mean(0); v["D0"][r] = (1 - nL / G) * z[L].var(0, ddof=1) / nL
        th["D0_fix1"][r] = e[L].mean(0) + Fb; v["D0_fix1"][r] = (1 - nL / G) * e[L].var(0, ddof=1) / nL
    df = {"T0": nr - 1, "T0_fix1": nr - 1, "D0": nL - 1, "D0_fix1": nL - 1}
    return th, v, df


def main_run(cfg_path, out):
    cfg = json.load(open(cfg_path)); os.makedirs(out, exist_ok=True)
    R, o = int(cfg.get("R", 2000)), int(cfg.get("o", 3))
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), cells=[], skipped=[])
    sp = os.path.join(out, "takeall_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    cv = pd.concat([pd.read_parquet(p) for p in cfg["cluster_values"]], ignore_index=True)
    rows = []
    for pop in cfg["populations"]:
        spot_cache = {}
        for est in pop["estimands"]:
            c = cv[(cv.task == pop["task"]) & (cv.encoder == pop["encoder"]) & (cv.scale == pop["scale"]) & (cv.estimand == est)]
            if not len(c):
                summ["skipped"].append(dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand=est,
                                            reason="no cluster values")); continue
            Z = c.pivot(index="donor", columns="gene", values="z").sort_index()
            F = c.pivot(index="donor", columns="gene", values="f").reindex(index=Z.index, columns=Z.columns)
            good = np.isfinite(Z.to_numpy(float)).all(0) & np.isfinite(F.to_numpy(float)).all(0)
            genes = [g for g, kk in zip(Z.columns, good) if kk]
            z, f = Z[genes].to_numpy(float), F[genes].to_numpy(float)
            donors = [str(d) for d in Z.index]; G = len(donors); theta = z.mean(0)
            key = tuple(donors)
            if key not in spot_cache:
                spot_cache[key] = probe_values(pop["spots_path"], pop["y_prefix"], pop.get("donor_col", "donor_id"), donors)
            spots, n_probe_genes = spot_cache[key]
            keys = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand=est)
            for k in cfg.get("k_grid", [1, 2]):
                for nL in cfg.get("nl_grid", [6, 8, 12]):
                    if nL - k < 4 or nL >= G:
                        summ["skipped"].append(dict(keys, k=k, n_L=nL, reason=f"n_L - k < 4 or n_L >= G (G = {G})")); continue
                    t0 = time.time()
                    tag = f"f3ta|{pop['task']}|{pop['encoder']}|{pop['scale']}|{est}|k{k}|nL{nL}"
                    th, v, df = run_cell(z, f, spots, k, nL, R, o, np.random.default_rng(zlib.crc32(tag.encode())))
                    for m in METHODS:
                        q = stats.t.ppf(1 - ALPHA / 2, df[m]); half = q * np.sqrt(np.maximum(v[m], 0))
                        cov = (np.abs(th[m] - theta[None, :]) <= half).mean(0)
                        ev = th[m].var(0, ddof=1)
                        for j, g in enumerate(genes):
                            rows.append(dict(**keys, gene=g, G=G, k=k, n_L=nL, method=m, R=R, theta=float(theta[j]),
                                             coverage=float(cov[j]), coverage_se=float(np.sqrt(cov[j] * (1 - cov[j]) / R)),
                                             mean_width=float(2 * half[:, j].mean()), median_width=float(2 * np.median(half[:, j])),
                                             bias=float(th[m][:, j].mean() - theta[j]), emp_var=float(ev[j]),
                                             ev_over_var=float(v[m][:, j].mean() / ev[j]) if ev[j] > 0 else np.nan))
                    info = dict(keys, G=G, n_genes=len(genes), n_genes_dropped=int((~good).sum()), n_probe_genes=n_probe_genes,
                                min_spots=int(min(len(s) for s in spots)), k=k, n_L=nL, seconds=round(time.time() - t0, 1))
                    summ["cells"].append(info); print(json.dumps(info), flush=True)
                    json.dump(summ, open(sp, "w"), indent=1, default=str)
    g = pd.DataFrame(rows, columns=GSCHEMA.names)
    out_cells = []
    if len(g):
        ck = ["task", "encoder", "scale", "estimand", "G", "k", "n_L"]
        w0 = g[g.method == "D0"][ck + ["gene", "mean_width"]].rename(columns={"mean_width": "w_D0"})
        w0f = g[g.method == "D0_fix1"][ck + ["gene", "mean_width"]].rename(columns={"mean_width": "w_D0f"})
        x = g.merge(w0, on=ck + ["gene"]).merge(w0f, on=ck + ["gene"])
        x["wr_D0"] = x.mean_width / x.w_D0
        x["wr_D0same"] = np.where(x.method.str.endswith("fix1"), x.mean_width / x.w_D0f, x.mean_width / x.w_D0)
        for sc in ("all", "r9_42"):
            y = x if sc == "all" else x[x.task.isin(R9_TASKS) & (x.gene.map(lambda s: zlib.crc32(s.encode()) % 7) == 0)]
            if not len(y):
                continue
            a = y.groupby(ck + ["method"]).agg(n_genes=("gene", "nunique"), median_coverage=("coverage", "median"),
                                               p10_coverage=("coverage", lambda s: float(np.quantile(s, 0.1))),
                                               median_width=("mean_width", "median"), median_wr_D0=("wr_D0", "median"),
                                               median_wr_D0same=("wr_D0same", "median")).reset_index()
            a.insert(4, "gene_scope", sc); out_cells.append(a)
    cells = pd.concat(out_cells, ignore_index=True) if out_cells else pd.DataFrame()
    summ.update(finished=time.strftime("%Y-%m-%dT%H:%M:%S"), n_gene_rows=len(g), n_cell_rows=len(cells))
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    cells.to_csv(os.path.join(out, "takeall_cells.csv"), index=False)
    pq.write_table(pa.Table.from_pandas(g, schema=GSCHEMA, preserve_index=False), os.path.join(out, "takeall_genes.parquet"))
    print(json.dumps({k: v for k, v in summ.items() if k not in ("config", "cells")}, indent=1, default=str)[:3000])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "anchor_check":
        raise SystemExit(anchor_check(*sys.argv[2:7]))
    raise SystemExit(main_run(sys.argv[2], sys.argv[3]))
