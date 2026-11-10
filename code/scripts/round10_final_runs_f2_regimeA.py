"""Round 10, track final-runs, F2.1: regime A design simulation over each task's own cluster values (plan, section 5.2).

A population is one (task, encoder, scale, estimand, gene): G donor values z_g with predictions f_g from
round10_final_runs_f2_cluster_values.py. For each n_L the driver draws R simple random samples of n_L clusters
without replacement (argsort of uniforms), the folds of the cross-fitted form being the first floor(n_L/2) and the
remaining labelled clusters of each draw. Every arm runs on the same draws; the bootstrap arms use the first R_boot.

usage: round10_final_runs_f2_regimeA.py <config.json> <out_dir>
config: cluster_values (list of parquet paths), select (dict of column -> list), n_grid, extra_n (task -> list),
        R, R_boot, B, boot_select (dict of column -> list), anchor_r9 (optional, see below), label.
Writes regimeA_summary.json first, then regimeA_cells.parquet (one row per population, n_L, arm and variance).
Anchor mode (config anchor_r9 = {"summary": <i34_williams_summary_hest.csv>}) replays round 9's generator
(default_rng(20261027) shared over (task, gene) in groupby order, one rng.random(R) consumed per n for FOLD) on mu,
uni_v2, log1p of CCRCC, INDIANA_KIDNEY and LUNG_XENIUM (LUNG genes with crc32 % 7 == 0), and compares FIX1 and
W_within summaries with round 9's file, writing regimeA_anchor_r9.csv.
"""
import json, os, sys, time, zlib
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from scipy import stats
import round10_final_runs_estimators as E

ALPHA = 0.10
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
KEYS = ["task", "encoder", "scale", "estimand", "gene"]
SCHEMA = pa.schema([(k, pa.string()) for k in KEYS] + [("G", pa.int64()), ("n", pa.int64()), ("arm", pa.string()),
                   ("variance", pa.string()), ("R", pa.int64()), ("theta", pa.float64()), ("bias", pa.float64()),
                   ("mcse_bias", pa.float64()), ("sd", pa.float64()), ("rmse", pa.float64()),
                   ("coverage", pa.float64()), ("coverage_se", pa.float64()), ("coverage_formed", pa.float64()),
                   ("frac_no_interval", pa.float64()), ("mean_width", pa.float64()), ("median_width", pa.float64()),
                   ("ev_over_var", pa.float64()), ("frac_v_neg", pa.float64())])


def seed_of(s):
    return zlib.crc32(s.encode())


def row(est, theta, lo=None, hi=None, ok=None, v=None):
    err = est - theta; R = len(est)
    if lo is None:
        lo = hi = np.full(R, np.nan); ok = np.zeros(R, bool)
    cov = ok & (lo <= theta) & (theta <= hi)
    w = (hi - lo)[ok]
    var = err.var()
    p = float(cov.mean())
    return dict(R=R, theta=float(theta), bias=float(err.mean()), mcse_bias=float(err.std() / np.sqrt(R)),
                sd=float(err.std()), rmse=float(np.sqrt((err ** 2).mean())), coverage=p,
                coverage_se=float(np.sqrt(p * (1 - p) / R)),
                coverage_formed=float(cov[ok].mean()) if ok.any() else np.nan,
                frac_no_interval=float(1 - ok.mean()), mean_width=float(w.mean()) if len(w) else np.nan,
                median_width=float(np.median(w)) if len(w) else np.nan,
                ev_over_var=float(np.mean(v) / var) if (v is not None and var > 0) else np.nan,
                frac_v_neg=float(np.mean(v < 0)) if v is not None else np.nan)


def tci(d, theta):
    lo, hi, ok = E.interval(d["est"], d["v"], d["df"]); return row(d["est"], theta, lo, hi, ok, d["v"])


def analytic(z, f, L, theta, tag):
    G, n = len(z), L.shape[1]; h = n // 2
    folds = [L[:, :h], L[:, h:]]
    out = []
    add = lambda arm, var, r: out.append(dict(arm=arm, variance=var, **r))
    add("classical", "fpc", tci(E.classical(z, f, L), theta))
    add("classical_nofpc", "nofpc", tci(E.classical(z, f, L, fpc=False), theta))
    fx = E.difference_fixed(z, f, L, 1.0)
    add("fix1", "fpc", tci(fx, theta))
    add("fix1_nofpc", "nofpc", tci(E.difference_fixed(z, f, L, 1.0, fpc=False), theta))
    for rule, nm in (("r5", "xf2_r5"), ("ols", "xf2_ols"), (1.0, "xf2_fix1")):
        for fpc in ((True, False) if rule == "r5" else (True,)):
            x = E.crossfit(z, f, folds, rule=rule, fpc=fpc)
            arm = nm if fpc else nm + "_nofpc"
            for var in ("V_w", "V", "V_max", "V_cons"):
                lo, hi, ok = E.interval(x["est"], x[var], x["df_w"])
                add(arm, var, row(x["est"], theta, lo, hi, ok, x[var]))
    for k, d in E.bh_variants(z, f, L).items():
        add(k, "own", tci(d, theta))
    # controls
    fc = np.full(G, f.mean())
    c1 = E.difference_fixed(z, fc, L, 1.0); c0 = E.classical(z, fc, L)
    dev = float(max(np.abs(c1["est"] - c0["est"]).max(), np.abs(c1["v"] - c0["v"]).max()))
    if dev > 1e-10 * max(1.0, np.abs(z).max() ** 2):
        raise SystemExit(f"constant-predictor identity failed for {tag}: {dev}")
    add("ctrl_const_fix1", "fpc", tci(c1, theta))
    perm = np.random.default_rng(seed_of(tag + "|perm")).permutation(G)
    fp = f[perm]
    add("ctrl_perm_fix1", "fpc", tci(E.difference_fixed(z, fp, L, 1.0), theta))
    x = E.crossfit(z, fp, folds, rule="r5")
    lo, hi, ok = E.interval(x["est"], x["V_w"], x["df_w"])
    add("ctrl_perm_xf2_r5", "V_w", row(x["est"], theta, lo, hi, ok, x["V_w"]))
    return out, dev


def bootstraps(z, f, L, theta, B, rng, chunk=200):
    """Around fix1. pairs percentile; wild cluster bootstrap-t (Webb six-point weights, unrestricted residuals);
    Rao and Wu's (1988) rescaled bootstrap-t with n-1 clusters resampled and the factor sqrt(1 - n/G)."""
    G = len(z); R, n = L.shape; fr = n / G; Fbar = f.mean()
    d = z[L] - f[L]; dbar = d.mean(1); s = d.std(1, ddof=1); se = np.sqrt((1 - fr) * s ** 2 / n)
    est = dbar + Fbar
    lo = {k: np.empty(R) for k in ("pairs", "wild", "raowu")}; hi = {k: np.empty(R) for k in lo}
    qa, qb = ALPHA / 2, 1 - ALPHA / 2
    for a in range(0, R, chunk):
        dd = d[a:a + chunk]; m = dd.shape[0]; db = dbar[a:a + chunk][:, None]; se_c = se[a:a + chunk]
        # pairs percentile
        ix = rng.integers(0, n, size=(m, B, n))
        bs = np.take_along_axis(dd[:, None, :].repeat(B, 1), ix, 2).mean(2) + Fbar
        lo["pairs"][a:a + m], hi["pairs"][a:a + m] = np.quantile(bs, qa, 1), np.quantile(bs, qb, 1)
        # wild bootstrap-t
        w = WEBB[rng.integers(0, 6, size=(m, B, n))]
        ds = db[:, :, None] + w * (dd - db)[:, None, :]
        tb = (ds.mean(2) - db) / np.sqrt((1 - fr) * ds.var(2, ddof=1) / n)
        tb = np.where(np.isfinite(tb), tb, np.nan)
        q1, q2 = np.nanquantile(tb, qa, 1), np.nanquantile(tb, qb, 1)
        lo["wild"][a:a + m] = est[a:a + m] - q2 * se_c; hi["wild"][a:a + m] = est[a:a + m] - q1 * se_c
        # Rao-Wu rescaled bootstrap-t, m* = n - 1
        ix = rng.integers(0, n, size=(m, B, n - 1))
        sel = np.take_along_axis(dd[:, None, :].repeat(B, 1), ix, 2)
        th = db + np.sqrt(1 - fr) * (sel.mean(2) - db)
        seb = np.sqrt((1 - fr) * sel.var(2, ddof=1) / n)
        tb = np.where(seb > 0, (th - db) / np.where(seb > 0, seb, 1), np.nan)
        q1, q2 = np.nanquantile(tb, qa, 1), np.nanquantile(tb, qb, 1)
        lo["raowu"][a:a + m] = est[a:a + m] - q2 * se_c; hi["raowu"][a:a + m] = est[a:a + m] - q1 * se_c
    out = []
    for k, nm in (("pairs", "boot_pairs_pct"), ("wild", "boot_wild_webb_t"), ("raowu", "boot_raowu_t")):
        ok = np.isfinite(lo[k]) & np.isfinite(hi[k])
        out.append(dict(arm=nm, variance="boot", **row(est, theta, lo[k], hi[k], ok)))
    return out


def selected(df, sel):
    m = np.ones(len(df), bool)
    for k, v in (sel or {}).items():
        m &= df[k].isin(v).to_numpy()
    return m


def run_anchor(cv, cfg, out):
    R = cfg["R"]; NS = [4, 6, 8, 10, 12, 16]
    a = cv[(cv.estimand == "mu") & (cv.encoder == "uni_v2") & (cv.scale == "log1p") &
           cv.task.isin(["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"])]
    rng = np.random.default_rng(20261027); rows = []
    for (task, gene), g in a.groupby(["task", "gene"]):
        if task == "LUNG_XENIUM" and (zlib.crc32(gene.encode()) % 7 != 0):
            continue
        g = g.sort_values("donor"); z = g.z.to_numpy(float); f = g.f.to_numpy(float); G = len(z)
        for n in NS:
            if n >= G:
                continue
            idx = np.argsort(rng.random((R, G)), axis=1); rng.random(R)
            L = idx[:, :n]; h = n // 2; th = z.mean()
            fx = E.difference_fixed(z, f, L, 1.0); x = E.crossfit(z, f, [L[:, :h], L[:, h:]], rule="r5")
            t1 = stats.t.ppf(1 - ALPHA / 2, n - 1); t2 = stats.t.ppf(1 - ALPHA / 2, n - 2)
            for form, est, v, tq in (("FIX1", fx["est"], fx["v"], t1), ("W_within", x["est"], x["V_w"], t2)):
                err = est - th; half = tq * np.sqrt(np.maximum(v, 0))
                rows.append(dict(task=task, gene=gene, n=n, form=form, coverage=float((np.abs(err) <= half).mean()),
                                 width=float(2 * half.mean()), rmse=float(np.sqrt((err ** 2).mean()))))
    r = pd.DataFrame(rows)
    s = r.groupby(["task", "form", "n"]).agg(pops=("gene", "size"), median_cov=("coverage", "median"),
                                             median_width=("width", "median"), median_rmse=("rmse", "median")).reset_index()
    ref = pd.read_csv(cfg["anchor_r9"]["summary"])
    m = s.merge(ref, on=["task", "form", "n"], suffixes=("", "_r9"))
    for c in ("pops", "median_cov", "median_width", "median_rmse"):
        m["d_" + c] = (m[c] - m[c + "_r9"]).abs()
    m.to_csv(os.path.join(out, "regimeA_anchor_r9.csv"), index=False)
    return dict(rows=len(m), expected=int(((ref.form.isin(["FIX1", "W_within"])) & ref.task.isin(["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"])).sum()),
                max_d_pops=float(m.d_pops.max()), max_d_cov=float(m.d_median_cov.max()),
                max_d_width=float(m.d_median_width.max()), max_d_rmse=float(m.d_median_rmse.max()))


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    sp = os.path.join(out, "regimeA_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    cv = pd.concat([pd.read_parquet(p) for p in cfg["cluster_values"]], ignore_index=True)
    if cfg.get("anchor_r9"):
        summ["anchor_r9"] = run_anchor(cv, cfg, out); json.dump(summ, open(sp, "w"), indent=1)
        print(json.dumps(summ["anchor_r9"]), flush=True)
        if cfg.get("anchor_only"):
            return
    cv = cv[selected(cv, cfg.get("select"))]
    R, Rb, B = cfg["R"], cfg["R_boot"], cfg["B"]
    rows, n_pop, n_skip, max_dev, t0 = [], 0, [], 0.0, time.time()
    for key, g in cv.groupby(KEYS, sort=True):
        g = g.sort_values("donor"); z = g.z.to_numpy(float); f = g.f.to_numpy(float); G = len(z)
        tagk = "|".join(key)
        if not (np.isfinite(z).all() and np.isfinite(f).all()):
            n_skip.append(tagk); continue
        n_pop += 1; theta = z.mean()
        boot = bool(selected(g.iloc[:1], cfg.get("boot_select")).all()) and Rb > 0
        ngrid = sorted(set(cfg["n_grid"]) | set(cfg.get("extra_n", {}).get(key[0], [])))
        for n in ngrid:
            if n >= G:
                continue
            tag = f"{tagk}|{n}"
            rng = np.random.default_rng(seed_of(tag))
            L = np.argsort(rng.random((R, G)), axis=1)[:, :n]
            res, dev = analytic(z, f, L, theta, tag); max_dev = max(max_dev, dev)
            if boot:
                res += bootstraps(z, f, L[:Rb], theta, B, np.random.default_rng(seed_of(tag + "|boot")))
            for r in res:
                rows.append(dict(zip(KEYS, key), G=G, n=n, **r))
        if n_pop % 50 == 0:
            print(f"{n_pop} populations, {len(rows)} rows, {time.time() - t0:.0f}s", flush=True)
    d = pd.DataFrame(rows, columns=SCHEMA.names)
    summ.update(n_populations=n_pop, n_skipped=len(n_skip), skipped=n_skip[:200], n_rows=len(d),
                max_const_identity_dev=max_dev, seconds=round(time.time() - t0, 1),
                finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(summ, open(sp, "w"), indent=1)
    pq.write_table(pa.Table.from_pandas(d, schema=SCHEMA, preserve_index=False), os.path.join(out, "regimeA_cells.parquet"))
    print(json.dumps({k: v for k, v in summ.items() if k != "config"}, indent=1))


if __name__ == "__main__":
    main()
