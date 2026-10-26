"""Round 9, track fewcluster, step I2-4: residual max-share of the real tasks against the frontiers.

Input: c0_cluster_summaries.csv.gz (Longleaf, results/round9/claude_science/C0_cluster_summaries/, gated-derived;
       stays on Longleaf). Columns used: task, encoder, gene, donor, mean_y, mean_f.
For each task (uni_v2; ACS_STATES with encoder pkg) and gene: kappa of the donor means (raw), kappa of the residual of
the least-squares fit of donor means on donor-mean predictions over all donors (predictions_before_run.md P1-P3),
the donor carrying the largest residual share, its residual z-score and leverage, and the frontiers at the task's
middle design size: kappa_star_v1 = kappa2(k*) (the definition the predictions were written with), kappa_sup =
kappa2(k*-1) (the corrected fixed-coefficient frontier), and an upper bound on the tuned-coefficient frontier from a
two-piece search with that gene's own prediction vector.
Outputs (aggregates only): i24_gene_kappa.csv, i24_task_summary.csv
Usage: python round9_fewcluster_hest_kappa.py <c0_cluster_summaries.csv.gz> <outdir>
"""
import sys, math
import numpy as np, pandas as pd
from scipy.special import comb

src, out = sys.argv[1], sys.argv[2]
ALPHA = 0.10
MID_N = {'CCRCC': 8, 'INDIANA_KIDNEY': 8, 'LUNG_XENIUM': 6, 'ACS_STATES': 8}
rng = np.random.default_rng(20261026)


def C(a, b):
    return comb(a, b, exact=True) if 0 <= b <= a else 0


def pi_k(G, n, k):
    return (C(G - k, n) + C(k, n)) / C(G, n)


def frontiers(G, n):
    ks = next((k for k in range(1, G // 2 + 1) if pi_k(G, n, k) <= ALPHA), None)
    v1 = (1 - ks / G) / ks
    sup = float('inf') if ks == 1 else (1 - (ks - 1) / G) / (ks - 1)
    return ks, v1, sup


def kap(e):
    d = e - e.mean(); ss = (d ** 2).sum()
    return float((d ** 2).max() / ss) if ss > 0 else float('nan')


def kappa_rows(E):
    D = E - E.mean(-1, keepdims=True); ss = (D ** 2).sum(-1)
    return (D ** 2).max(-1) / np.where(ss > 0, ss, np.nan)


def tuned_upper(f, ks, n_random=1500, n_phi=121, n_local=150):
    G = len(f); ft = (f - f.mean()) / f.std()
    X = np.c_[np.ones(G), ft]; P = np.eye(G) - X @ np.linalg.pinv(X)
    phis = np.linspace(0, np.pi, n_phi, endpoint=False)
    shape = np.cos(phis)[:, None] + np.sin(phis)[:, None] * ft[None, :]
    order = np.argsort(f)

    def best_for(sets):
        M = np.zeros((len(sets), G))
        for i, s in enumerate(sets):
            M[i, s] = 1.0
        K = kappa_rows((M[:, None, :] * shape[None, :, :]) @ P)
        K = np.where(np.isnan(K), np.inf, K)
        i, j = np.unravel_index(np.argmin(K), K.shape)
        return K[i, j], sets[i]

    best = np.inf
    for k in range(1, ks):
        cands = [order[i:i + k] for i in range(G - k + 1)] + [rng.choice(G, k, replace=False) for _ in range(n_random)]
        cur = (np.inf, None)
        for st in range(0, len(cands), 500):
            r = best_for(cands[st:st + 500])
            if r[0] < cur[0]:
                cur = r
        kv, s = cur
        for _ in range(n_local if k > 1 else 0):
            s2 = list(s); s2[rng.integers(k)] = rng.choice([g for g in range(G) if g not in s])
            r = best_for([np.array(s2)])
            if r[0] < kv:
                kv, s = r
        best = min(best, kv)
    return best


d = pd.read_csv(src)
d = d[((d.encoder == 'uni_v2') & d.task.isin(['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM'])) |
      ((d.task == 'ACS_STATES') & (d.encoder == 'pkg'))]
rows = []
for (task, enc, gene), g in d.groupby(['task', 'encoder', 'gene']):
    g = g.sort_values('donor')
    y = g.mean_y.to_numpy(float); f = g.mean_f.to_numpy(float); G = len(y)
    X = np.c_[np.ones(G), f]; H = X @ np.linalg.pinv(X); r = y - H @ y
    i = int(np.argmax((r - r.mean()) ** 2))
    n = MID_N[task]; ks, v1, sup = frontiers(G, n)
    rows.append(dict(task=task, encoder=enc, gene=gene, G=G, n_mid=n, kappa_raw=kap(y), kappa_resid=kap(r),
                     argmax_donor=str(g.donor.iloc[i]), argmax_resid_z=float(r[i] / r.std(ddof=2)),
                     argmax_leverage=float(H[i, i]), kappa_star_v1=v1, kappa_sup=sup,
                     tuned_frontier_upper=tuned_upper(f, ks)))
gk = pd.DataFrame(rows)
gk['beyond_v1'] = gk.kappa_resid > gk.kappa_star_v1
gk['beyond_sup'] = gk.kappa_resid > gk.kappa_sup
gk['beyond_tuned'] = gk.kappa_resid > gk.tuned_frontier_upper
gk.to_csv(f'{out}/i24_gene_kappa.csv', index=False)
summ = gk.groupby(['task', 'encoder']).agg(n_genes=('gene', 'size'), G=('G', 'first'), n_mid=('n_mid', 'first'),
                                           median_kappa_raw=('kappa_raw', 'median'),
                                           median_kappa_resid=('kappa_resid', 'median'),
                                           kappa_star_v1=('kappa_star_v1', 'first'), kappa_sup=('kappa_sup', 'first'),
                                           median_tuned_frontier_upper=('tuned_frontier_upper', 'median'),
                                           frac_beyond_v1=('beyond_v1', 'mean'), frac_beyond_sup=('beyond_sup', 'mean'),
                                           frac_beyond_tuned=('beyond_tuned', 'mean'),
                                           top_argmax_donor=('argmax_donor', lambda s: s.value_counts().index[0]),
                                           frac_top_argmax=('argmax_donor', lambda s: s.value_counts().iloc[0] / len(s)),
                                           median_argmax_leverage=('argmax_leverage', 'median')).reset_index()
summ.to_csv(f'{out}/i24_task_summary.csv', index=False)
print(summ.to_string(index=False))
