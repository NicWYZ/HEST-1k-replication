"""Round 9 (claude-science): probe, then a take-all stratum of probe-atypical donors, then simple random selection.

Runs on Longleaf; aggregates only. Probe o = 3 spots per donor gives u_hat_g (mean over genes and probe spots of y).
The k donors with the largest |u_hat_g - median u_hat| are labelled with certainty; n_L - k more are drawn at random
from the other G - k. theta_j = mean over all donors of the donor mean of y_j.
  T0: (sum over take-all donors + (G - k) * mean of sampled rest) / G; variance from the rest only (df n_L - k - 1)
  T2: same with a regression estimator on u_hat within the rest (df n_L - k - 2)
D0 (plain mean of an SRS of n_L donors) is recomputed in the same draws for the width ratio.
Usage: python round9_probe_takeall.py <parquet> <task> <outdir> [reps]
"""
import sys, numpy as np, pandas as pd
from scipy import stats

def main(pq, task, out, reps=400, o=3):
    df = pd.read_parquet(pq)
    genes = [c[3:] for c in df.columns if c.startswith("y__")]
    Y = df[["y__" + g for g in genes]].values.astype(float)
    d = df.donor_id.astype(str).values; ud = sorted(set(d)); G = len(ud)
    idx = [np.where(d == x)[0] for x in ud]
    Ybar = np.array([Y[i].mean(0) for i in idx]); theta = Ybar.mean(0)
    rng = np.random.default_rng(20261027); rows = []
    for k in (1, 2):
        for nL in (6, 8, 12):
            if nL - k < 4 or nL >= G: continue
            acc = {m: [np.zeros(len(genes)), np.zeros(len(genes))] for m in ("D0", "T0", "T2")}
            for r in range(reps):
                uhat = np.array([Y[rng.choice(i, o, replace=False)].mean() for i in idx])
                dev = np.abs(uhat - np.median(uhat)); C = np.argsort(-dev)[:k]
                rest = np.setdiff1d(np.arange(G), C); Nr = len(rest); nr = nL - k
                S = np.sort(rng.choice(rest, nr, replace=False)); yS = Ybar[S]
                # D0
                L = np.sort(rng.choice(G, nL, replace=False)); yL = Ybar[L]
                e = yL.mean(0); se = np.sqrt((1 - nL / G) * yL.var(0, ddof=1) / nL); q = stats.t.ppf(0.95, nL - 1)
                acc["D0"][0] += np.abs(e - theta) <= q * se; acc["D0"][1] += 2 * q * se
                # T0
                restmean = yS.mean(0); se_r = np.sqrt((1 - nr / Nr) * yS.var(0, ddof=1) / nr)
                e = (Ybar[C].sum(0) + Nr * restmean) / G; se = Nr / G * se_r; q = stats.t.ppf(0.95, nr - 1)
                acc["T0"][0] += np.abs(e - theta) <= q * se; acc["T0"][1] += 2 * q * se
                # T2
                A = np.column_stack([np.ones(nr), uhat[S]]); B = np.linalg.lstsq(A, yS, rcond=None)[0]
                est_rest = np.array([1.0, uhat[rest].mean()]) @ B; res = yS - A @ B
                se_r = np.sqrt((1 - nr / Nr) * (res ** 2).sum(0) / (nr - 2) / nr)
                e = (Ybar[C].sum(0) + Nr * est_rest) / G; se = Nr / G * se_r; q = stats.t.ppf(0.95, nr - 2)
                acc["T2"][0] += np.abs(e - theta) <= q * se; acc["T2"][1] += 2 * q * se
            for m, (cv, w) in acc.items():
                for j, g in enumerate(genes):
                    rows.append(dict(task=task, k=k, n_L=nL, method=m, gene=g, coverage=cv[j] / reps, mean_width=w[j] / reps))
            print(task, k, nL, flush=True)
    pd.DataFrame(rows).to_csv(f"{out}/takeall_by_gene__{task}.csv.gz", index=False)

if __name__ == "__main__":
    a = sys.argv; main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 400)
