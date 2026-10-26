"""Round 9 (claude-science): probe-then-label feasibility on real tasks (runs on Longleaf; aggregates only).

Design target theta_j = mean over all G donors of the donor mean of y_j. Each replicate: a probe of o random spots in
every donor gives u_hat_g = mean over genes and probe spots of y; a simple random sample of n_L donors is fully
labelled. Estimators (90% t intervals, finite-population factor 1 - n_L/G):
  D0 mean of labelled donor means (df n_L - 1)
  D1 regression on the donor-mean prediction (df n_L - 2)
  D2 regression on u_hat (df n_L - 2)
  D3 regression on u_hat and the donor-mean prediction (df n_L - 3)
Usage: python round9_probe_feasibility.py <parquet> <task> <outdir> [reps]
"""
import sys, numpy as np, pandas as pd
from scipy import stats

def reg_est(ybar_L, X_L, X_all, G):
    n = len(ybar_L); k = X_L.shape[1]
    A = np.column_stack([np.ones(n), X_L]); B = np.linalg.lstsq(A, ybar_L, rcond=None)[0]   # (k+1) x J
    Aall = np.column_stack([np.ones(len(X_all)), X_all])
    est = Aall.mean(0) @ B                     # = ybar_L + b'(xbar_all - xbar_L)
    res = ybar_L - A @ B
    df = n - k - 1
    s2 = (res ** 2).sum(0) / df
    se = np.sqrt((1 - n / G) * s2 / n)
    return est, se, df

def main(pq, task, out, reps=400):
    df = pd.read_parquet(pq)
    genes = [c[3:] for c in df.columns if c.startswith("y__")]
    Y = df[["y__" + g for g in genes]].values.astype(float); F = df[["f__" + g for g in genes]].values.astype(float)
    d = df.donor_id.astype(str).values; ud = sorted(set(d)); G = len(ud)
    idx = [np.where(d == x)[0] for x in ud]
    Ybar = np.array([Y[i].mean(0) for i in idx]); Fbar = np.array([F[i].mean(0) for i in idx])
    theta = Ybar.mean(0)
    rng = np.random.default_rng(20261026)
    rows = []
    for o in (1, 3):
        for nL in (4, 6, 8, 12):
            if nL >= G: continue
            cov = {m: np.zeros(len(genes)) for m in ("D0", "D1", "D2", "D3")}
            wid = {m: np.zeros(len(genes)) for m in cov}
            for r in range(reps):
                uhat = np.array([Y[rng.choice(i, o, replace=False)].mean() for i in idx])
                L = np.sort(rng.choice(G, nL, replace=False))
                yL = Ybar[L]
                # D0
                se0 = np.sqrt((1 - nL / G) * yL.var(0, ddof=1) / nL); est0 = yL.mean(0); q0 = stats.t.ppf(0.95, nL - 1)
                outs = {"D0": (est0, se0, q0)}
                for m, XL, Xa in (("D1", None, None), ("D2", uhat[L][:, None], uhat[:, None]), ("D3", None, None)):
                    if m == "D1":
                        est = np.empty(len(genes)); se = np.empty(len(genes))
                        for j in range(len(genes)):
                            e, s, dfr = reg_est(yL[:, j], Fbar[L, j][:, None], Fbar[:, j][:, None], G); est[j], se[j] = e, s
                        outs[m] = (est, se, stats.t.ppf(0.95, nL - 2))
                    elif m == "D2":
                        e, s, dfr = reg_est(yL, XL, Xa, G); outs[m] = (e, s, stats.t.ppf(0.95, dfr))
                    else:
                        if nL - 3 < 1: continue
                        est = np.empty(len(genes)); se = np.empty(len(genes))
                        for j in range(len(genes)):
                            X2L = np.column_stack([uhat[L], Fbar[L, j]]); X2 = np.column_stack([uhat, Fbar[:, j]])
                            e, s, dfr = reg_est(yL[:, j], X2L, X2, G); est[j], se[j] = e, s
                        outs[m] = (est, se, stats.t.ppf(0.95, nL - 3))
                for m, (e, s, q) in outs.items():
                    cov[m] += (np.abs(e - theta) <= q * s); wid[m] += 2 * q * s
            for m in cov:
                if wid[m].sum() == 0: continue
                for j, g in enumerate(genes):
                    rows.append(dict(task=task, o=o, n_L=nL, method=m, gene=g, coverage=cov[m][j] / reps, mean_width=wid[m][j] / reps))
            print(task, o, nL, flush=True)
    pd.DataFrame(rows).to_csv(f"{out}/probe_by_gene__{task}.csv.gz", index=False)

if __name__ == "__main__":
    a = sys.argv; main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 400)
