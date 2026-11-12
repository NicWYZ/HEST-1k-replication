"""Round 10, track final-runs, F3.3 (iv): rej_t and the cube design matched against simple random selection
(plan, section 5d.3 (iv); R7-7 as decided at L3).

A population is one (task, encoder, scale, estimand): the G donor values z_g and predictions f_g of F2's cluster values
(round10_final_runs_f2_cluster_values.py), genes with any non-finite value dropped. Per n_L (skipped when n_L > G - 2):

  D0     simple random sampling. Draw d is candidate 0 of D2's candidate stream for d.
  D2     rejective sampling on the Mahalanobis distance of the labelled mean of the balance variable (round 5's
         round5_ppi_balance.mahalanobis_pool), balance 'own' = fbar_g per gene, p_a in {0.1, 0.01}. Candidate k of draw
         d is the first n_L of argsort of uniforms from default_rng(crc32('<tag>|d<d>')), drawn in batches of BATCH;
         the threshold is the p_a quantile of the distance over a pool of the first POOL candidates of every draw, as
         round 5's E4b; per gene the first candidate at or below the threshold is accepted. Runs only where the
         support p_a C(G, n_L) >= 1000; other cells are recorded as unsupported.
  D2lim  the limit, D2 on two balance variables, on the HEST tasks only (donor mean embeddings exist only there):
         'own_pcE1' = (fbar_g, the first principal component of the round 4 Q5 mean embeddings) and 'pcE2' = round 5's
         two-component embedding balance. The plan's wording ('fbar_g and pcE2') admits both readings; see the F3
         return notes. Same support rule.
  cube   round 7's S4b cube design (round7_ppi_s4b_cube3: target_pi of |fbar_g - Fbar|, balance (pi_g, 1, fbar_g),
         pi_gh simulated with R_for(G, n_L) cube draws, then D evaluation draws), seeds '<tag>|cube|pi' and
         '<tag>|cube|eval'.

Estimators, on the same draws within each design:
  classical  D0: labelled mean, (1 - n/G) s^2/n, t_{n-1} ('srs_t'). D2: round 5's rej_t on z_g ('rej_t'), and the
             srs_t interval beside. cube: round 7's intervals_p on z_g (HT and Hajek; variance 'sim' with t_{n-rank}
             'res' and t_{n-2} 'n2', and the residual form 'res').
  fix1       D0: difference estimator with coefficient 1 (round10_final_runs_estimators.difference_fixed). D2: rej_t on
             e_g = z_g - f_g with Fbar_U added, and srs_t on e_g beside. cube: intervals_p on e_g with Fbar_U added to
             the HT and Hajek point estimates.
Seeds: zlib.crc32 of 'f3bal|<task>|<encoder>|<scale>|<estimand>|nL<n>' extended by the design part.

usage: round10_final_runs_f3_balance.py <config.json> <out_dir>
config: cluster_values {path list}, populations [{task, encoder, scale, estimands, vtag (embeddings), nl_grid}],
        draws, pool, batch, r_cap, designs (subset of D0, D2, D2lim, cube), root.
Writes balance_summary.json first, then balance_cells.csv (per cell medians over genes, both gene scopes, with width
ratios to D0 under the same estimator and to D0 classical) and balance_genes.parquet.
"""
import json, math, os, sys, time, zlib
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from scipy import stats
import round5_ppi_balance as BAL
from round5_ppi_e4_selection import pcs, embeddings
import round7_ppi_s4b_cube3 as S4B
from round7_ppi_s3_cube import target_pi, R_for

ALPHA = 0.10
PAS = (0.1, 0.01)
R9_TASKS = ("LUNG_XENIUM",)
HEST = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM")
CUBE_KEYS = (("H", "sim", "res"), ("HT", "sim", "res"), ("H", "sim", "n2"), ("H", "res", "res"))
STATS = ("coverage", "coverage_all", "share_formed", "share_neg", "width_mean", "width_median", "emp_var", "est_var_mean",
         "bias", "bias_z")
GSCHEMA = pa.schema([(k, pa.string()) for k in ("task", "encoder", "scale", "estimand", "gene")] +
                    [("G", pa.int64()), ("n_L", pa.int64())] +
                    [(k, pa.string()) for k in ("design", "balance")] + [("p_a", pa.float64())] +
                    [(k, pa.string()) for k in ("estimator", "variance")] + [("n_draws", pa.int64())] +
                    [(k, pa.float64()) for k in STATS])


def seed(s):
    return zlib.crc32(s.encode())


def gene_stats(th, v, df, theta):
    """th, v (D, ng); df scalar or (D, ng); theta (ng). Round 7's convention (round7_ppi_weighting.summarise): an
    interval is formed where th and v are finite and df >= 2, a negative v is set to 0 and counted. coverage is over
    formed draws, coverage_all counts a draw with no interval as a miss; widths are over formed draws."""
    df = np.broadcast_to(np.asarray(df, float), th.shape)
    ok = np.isfinite(v) & np.isfinite(th) & (df >= 2)
    neg = ok & (v < 0)
    with np.errstate(invalid="ignore"):
        q = stats.t.ppf(1 - ALPHA / 2, np.where(df >= 1, df, np.nan))
    vv = np.where(ok, np.maximum(np.where(ok, v, 0.0), 0.0), np.nan)
    half = np.where(ok, q * np.sqrt(np.where(ok, vv, 0.0)), np.nan)
    cov = ok & (np.abs(th - theta[None, :]) <= half)
    nf = ok.sum(0)
    w = np.where(ok, 2 * half, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        thf = np.where(np.isfinite(th), th, np.nan)
        ev = np.nanvar(thf, axis=0, ddof=1)
        bias = np.nanmean(thf, 0) - theta
        out = dict(coverage=np.where(nf > 0, cov.sum(0) / np.maximum(nf, 1), np.nan), coverage_all=cov.mean(0),
                   share_formed=ok.mean(0), share_neg=neg.sum(0) / np.maximum(nf, 1),
                   width_mean=np.where(nf > 0, np.nansum(w, 0) / np.maximum(nf, 1), np.nan),
                   width_median=np.array([np.median(w[ok[:, j], j]) if nf[j] else np.nan for j in range(th.shape[1])]),
                   emp_var=ev, est_var_mean=np.where(nf > 0, np.nansum(vv, 0) / np.maximum(nf, 1), np.nan),
                   bias=bias, bias_z=bias / np.sqrt(ev / np.isfinite(thf).sum(0)))
    return out


def srs(zl, G):
    n = zl.shape[-1]
    return zl.mean(-1), (1 - n / G) * zl.var(-1, ddof=1) / n, float(n - 1)


class Candidates:
    """Candidate k of draw d: the first n of argsort(default_rng(crc32('<tag>|d<d>')).random(G)), batch by batch."""

    def __init__(self, tag, G, n, draws, batch):
        self.tag, self.G, self.n, self.batch = tag, G, n, batch
        self.rngs = [np.random.default_rng(seed(f"{tag}|d{d}")) for d in range(draws)]
        self.first = np.stack([np.argsort(r.random((batch, G)), axis=1)[:, :n] for r in self.rngs]).astype(np.int16)
        self.more = {}                       # d -> list of further batches

    def batch_of(self, d, b):
        if b == 0:
            return self.first[d]
        L = self.more.setdefault(d, [])
        while len(L) < b:
            L.append(np.argsort(self.rngs[d].random((self.batch, self.G)), axis=1)[:, :self.n].astype(np.int16))
        return L[b - 1]

    def cand(self, d, k):
        return self.batch_of(d, k // self.batch)[k % self.batch]


def masks(idx, G):
    m = np.zeros((idx.shape[0], G), bool)
    np.put_along_axis(m, idx.astype(np.int64), True, axis=1)
    return m


def d2_accept(C, X, pool, pas, chunk_d=100, chunk_c=50):
    """X (G, ncol, k). Returns {p_a: (D, ncol) accepted candidate index}, thresholds {p_a: (ncol,)} and the number of
    further candidate batches scanned. Columns are processed in chunks of chunk_c."""
    D = len(C.rngs); ncol = X.shape[1]
    acc = {p_: np.full((D, ncol), -1, np.int64) for p_ in pas}
    thr = {p_: np.full(ncol, np.nan) for p_ in pas}
    n_ext = 0
    for c0 in range(0, ncol, chunk_c):
        cs = slice(c0, min(ncol, c0 + chunk_c)); Xc = X[:, cs, :]
        parts = []
        for d0 in range(0, D, chunk_d):
            mk = masks(C.first[d0:d0 + chunk_d, :pool].reshape(-1, C.n), C.G)
            with np.errstate(invalid="ignore", divide="ignore"):
                parts.append(BAL.mahalanobis_pool(mk, Xc))
        P = np.concatenate(parts, 0); del parts
        P = np.where(np.isfinite(P), P, np.nan)
        for p_ in pas:
            thr[p_][cs] = np.nanquantile(P, p_, axis=0)
        del P
        for d0 in range(0, D, chunk_d):
            nd = min(chunk_d, D - d0)
            mk = masks(C.first[d0:d0 + nd].reshape(-1, C.n), C.G)
            with np.errstate(invalid="ignore", divide="ignore"):
                dist = BAL.mahalanobis_pool(mk, Xc).reshape(nd, C.batch, -1)
            for p_ in pas:
                ok = dist <= thr[p_][cs][None, None, :]
                acc[p_][d0:d0 + nd, cs] = np.where(ok.any(1), ok.argmax(1), -1)
        for p_ in pas:
            sub = acc[p_][:, cs]
            for d in np.flatnonzero((sub < 0).any(1)):
                b = 1
                while (acc[p_][d, cs] < 0).any():
                    mk = masks(C.batch_of(d, b), C.G)
                    with np.errstate(invalid="ignore", divide="ignore"):
                        dist = BAL.mahalanobis_pool(mk, Xc)
                    ok = dist <= thr[p_][cs][None, :]
                    cur = acc[p_][d, cs]
                    hit = ok.any(0) & (cur < 0)
                    cur[hit] = b * C.batch + ok[:, hit].argmax(0)
                    acc[p_][d, cs] = cur
                    b += 1; n_ext += 1
                    if b * C.batch > 2_000_000:
                        raise RuntimeError(f"no accepted candidate after 2,000,000 candidates, draw {d}")
    return acc, thr, n_ext


def labelled_idx(C, acc_d):
    """acc_d (D, ncol) accepted candidate per draw and column -> (D, ncol, n) donor indices."""
    D, ncol = acc_d.shape
    out = np.empty((D, ncol, C.n), np.int64)
    for d in range(D):
        for k in np.unique(acc_d[d]):
            out[d, acc_d[d] == k] = C.cand(d, int(k))
    return out


def run_srs_like(z, f, idx, G, X=None, p_a=None):
    """idx (D, ncol, n). Returns {(estimator, variance): (th, v, df)} with srs_t for both, rej_t when X is given."""
    D, ncol, n = idx.shape
    cols = np.arange(ncol)[None, :, None]
    zl, fl = z.T[cols, idx], f.T[cols, idx]
    Fb = f.mean(0)
    out = {}
    th, v, df = srs(zl, G); out[("classical", "srs_t")] = (th, v, df)
    th, v, df = srs(zl - fl, G); out[("fix1", "srs_t")] = (th + Fb[None, :], v, df)
    if X is not None:
        e = z - f
        tc, vc, tf, vf = (np.empty((D, ncol)) for _ in range(4))
        dfr = None
        for d in range(D):
            Lm = np.zeros((G, ncol), bool); Lm[idx[d].T, np.arange(ncol)[None, :]] = True
            tc[d], vc[d], dfr = BAL.rej_t(z, X, Lm, p_a)
            tf[d], vf[d], _ = BAL.rej_t(e, X, Lm, p_a)
        out[("classical", "rej_t")] = (tc, vc, dfr)
        out[("fix1", "rej_t")] = (tf + Fb[None, :], vf, dfr)
    return out


def add(rows, keys, genes, G, n, design, balance, p_a, res, theta):
    for (est, var), (th, v, df) in res.items():
        s = gene_stats(th, v, df, theta)
        for j, g in enumerate(genes):
            rows.append(dict(**keys, gene=g, G=G, n_L=n, design=design, balance=balance, p_a=p_a, estimator=est,
                             variance=var, n_draws=int(th.shape[0]), **{k: float(s[k][j]) for k in STATS}))


def cell_table(g):
    """Per cell medians over genes and width ratios to D0 under the same estimator and to D0 classical."""
    cellk = ["task", "encoder", "scale", "estimand", "gene_scope", "G", "n_L"]
    d0 = g[(g.design == "D0")][["task", "encoder", "scale", "estimand", "n_L", "gene", "estimator", "width_mean"]]
    d0s = d0.rename(columns={"width_mean": "w_D0_same"})
    d0c = d0[d0.estimator == "classical"].drop(columns="estimator").rename(columns={"width_mean": "w_D0cl"})
    k = ["task", "encoder", "scale", "estimand", "n_L", "gene"]
    x = g.merge(d0s, on=k + ["estimator"], how="left").merge(d0c, on=k, how="left")
    x["wr_D0same"] = x.width_mean / x.w_D0_same; x["wr_D0cl"] = x.width_mean / x.w_D0cl
    out = []
    for sc in ("all", "r9_42"):
        y = x if sc == "all" else x[x.task.isin(R9_TASKS) & (x.gene.map(lambda s: zlib.crc32(s.encode()) % 7) == 0)]
        if not len(y):
            continue
        y = y.assign(gene_scope=sc, p_a=y.p_a.fillna(-1))
        a = y.groupby(cellk + ["design", "balance", "p_a", "estimator", "variance"]).agg(
            n_genes=("gene", "nunique"), coverage_median=("coverage", "median"), coverage_all_median=("coverage_all", "median"),
            share_formed_min=("share_formed", "min"), width_median=("width_mean", "median"),
            wr_D0same=("wr_D0same", "median"), wr_D0cl=("wr_D0cl", "median"),
            share_abs_bias_z_gt3=("bias_z", lambda b: float(np.mean(np.abs(b) > 3)))).reset_index()
        a["p_a"] = a.p_a.replace(-1, np.nan)
        out.append(a)
    return pd.concat(out, ignore_index=True)


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    D, POOL, BATCH = int(cfg.get("draws", 2000)), int(cfg.get("pool", 500)), int(cfg.get("batch", 1000))
    designs = cfg.get("designs", ["D0", "D2", "D2lim", "cube"])
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), cells=[], skipped=[])
    sp = os.path.join(out, "balance_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    cv = pd.concat([pd.read_parquet(p) for p in cfg["cluster_values"]], ignore_index=True)
    rows = []
    for pop in cfg["populations"]:
        for est in pop["estimands"]:
            c = cv[(cv.task == pop["task"]) & (cv.encoder == pop["encoder"]) & (cv.scale == pop["scale"]) & (cv.estimand == est)]
            if not len(c):
                summ["skipped"].append(dict(pop, estimand=est, reason="no cluster values")); continue
            Z = c.pivot(index="donor", columns="gene", values="z").sort_index()
            F = c.pivot(index="donor", columns="gene", values="f").reindex(index=Z.index, columns=Z.columns)
            good = np.isfinite(Z.to_numpy(float)).all(0) & np.isfinite(F.to_numpy(float)).all(0)
            genes = [g for g, k in zip(Z.columns, good) if k]
            z, f = Z[genes].to_numpy(float), F[genes].to_numpy(float)
            donors = list(Z.index); G, ng = z.shape; theta = z.mean(0)
            keys = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand=est)
            emb = None
            if "D2lim" in designs and pop["task"] in HEST:
                E_ = embeddings(cfg.get("root", "/work/users/w/e/weiyang/hest_replication"), pop.get("vtag", pop["task"]),
                                pop["encoder"], donors)
                emb = pcs(E_, 2) if E_ is not None and np.isfinite(E_).all() else None
            for n in pop.get("nl_grid", cfg.get("nl_grid", [4, 6, 8, 12])):
                t0 = time.time()
                if n > G - 2:
                    summ["skipped"].append(dict(keys, n_L=n, reason=f"n_L > G - 2 (G = {G})")); continue
                tag = f"f3bal|{pop['task']}|{pop['encoder']}|{pop['scale']}|{est}|nL{n}"
                info = dict(keys, G=G, n_genes=ng, n_genes_dropped=int((~good).sum()), n_L=n, support={})
                C = Candidates(tag, G, n, D, BATCH)
                d0idx = np.broadcast_to(C.first[:, 0][:, None, :], (D, ng, n)).astype(np.int64)
                if "D0" in designs:
                    add(rows, keys, genes, G, n, "D0", "none", np.nan, run_srs_like(z, f, d0idx, G), theta)
                bals = {}
                if "D2" in designs:
                    bals["own"] = ("D2", f[:, :, None])
                if emb is not None:
                    bals["own_pcE1"] = ("D2lim", np.concatenate([f[:, :, None], np.broadcast_to(emb[:, None, :1], (G, ng, 1))], 2))
                    bals["pcE2"] = ("D2lim", emb[:, None, :])
                for b, (dname, X) in bals.items():
                    pas = [p_ for p_ in PAS if p_ * math.comb(G, n) >= 1000]
                    for p_ in PAS:
                        info["support"][f"{b}|{p_}"] = p_ * math.comb(G, n)
                    if not pas:
                        summ["skipped"].append(dict(keys, n_L=n, design=dname, balance=b, reason="support < 1000 at both p_a"))
                        continue
                    acc, thr, n_ext = d2_accept(C, X, POOL, pas)
                    info[f"ext_batches|{b}"] = n_ext
                    for p_ in pas:
                        a = acc[p_] if acc[p_].shape[1] == ng else np.broadcast_to(acc[p_], (D, ng))
                        info[f"cand_mean|{b}|{p_}"] = float(a.mean() + 1)
                        idx = labelled_idx(C, a)
                        res = run_srs_like(z, f, idx, G, X, p_)
                        info[f"acc2|{b}|{p_}"] = float(np.nanmax(np.abs(res[("classical", "rej_t")][0] - res[("classical", "srs_t")][0])))
                        add(rows, keys, genes, G, n, dname, b, p_, res, theta)
                    for p_ in PAS:
                        if p_ not in pas:
                            summ["skipped"].append(dict(keys, n_L=n, design=dname, balance=b, p_a=p_, reason="support < 1000"))
                info["seconds_srs_d2"] = round(time.time() - t0, 1)
                if "cube" in designs:
                    tc = time.time()
                    pit = target_pi(np.abs(f - f.mean(0, keepdims=True)), n)
                    R = min(R_for(G, n), int(cfg.get("r_cap", 1_000_000)))
                    st = S4B.pi_sim_p(pit, f, R, f"{tag}|cube|pi")
                    pih = st["cnt"] / R; pgh = st["pair"] / R
                    L, rf, rN = S4B.eval_p(pit, f, D, f"{tag}|cube|eval")
                    Fb = f.mean(0)
                    ivc, _, rank = S4B.intervals_p(z, f, L, pih, pit, pgh, G, n)
                    ivf, _, _ = S4B.intervals_p(z - f, f, L, pih, pit, pgh, G, n)
                    res = {}
                    for kk in CUBE_KEYS:
                        th, v, df, _ = ivc[kk]; res[("classical", "|".join(kk))] = (th, v, df)
                        th, v, df, _ = ivf[kk]; res[("fix1", "|".join(kk))] = (th + Fb[None, :], v, df)
                    add(rows, keys, genes, G, n, "cube", "pi,1,own", np.nan, res, theta)
                    info.update(cube_R=R, cube_resid_f_max=float(rf.max()), cube_resid_N_max=float(rN.max()),
                                cube_rank_median=float(np.median(rank)), seconds_cube=round(time.time() - tc, 1))
                info["seconds"] = round(time.time() - t0, 1)
                summ["cells"].append(info)
                print(json.dumps({k: info[k] for k in ("task", "encoder", "scale", "estimand", "n_L", "seconds")}), flush=True)
                json.dump(summ, open(sp, "w"), indent=1, default=str)
    g = pd.DataFrame(rows, columns=GSCHEMA.names)
    cells = cell_table(g) if len(g) else pd.DataFrame()
    summ.update(finished=time.strftime("%Y-%m-%dT%H:%M:%S"), n_gene_rows=len(g), n_cell_rows=len(cells))
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    cells.to_csv(os.path.join(out, "balance_cells.csv"), index=False)
    pq.write_table(pa.Table.from_pandas(g, schema=GSCHEMA, preserve_index=False), os.path.join(out, "balance_genes.parquet"))
    print(json.dumps({k: v for k, v in summ.items() if k not in ("config", "cells")}, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
