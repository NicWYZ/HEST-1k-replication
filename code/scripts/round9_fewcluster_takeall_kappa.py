"""Round 9, track fewcluster, step I2-3: residual max-share of CCRCC after a take-all stratum.

Input: c0_cluster_summaries.csv.gz (Longleaf). For each CCRCC gene (uni_v2): residual max-share of the donor means on
donor-mean predictions after removing (a) INT5 and (b) the donor with the largest residual for that gene, refitted on
the remaining 23 donors; compared with the frontier of 7 of 23 at alpha = 0.10 (kappa2(k*-1)).
Predictions: results/round9/fewcluster/design/predictions_before_run.md. Output: i23_takeall_kappa.csv (per gene),
i23_takeall_summary.csv.
"""
import sys
import numpy as np, pandas as pd
from scipy.special import comb
src, out = sys.argv[1], sys.argv[2]


def frontier(G, n, a=0.10):
    pi = lambda k: (comb(G - k, n, exact=True) + (comb(k, n, exact=True) if k >= n else 0)) / comb(G, n, exact=True)
    ks = next(k for k in range(1, G // 2 + 1) if pi(k) <= a)
    return float('inf') if ks == 1 else (1 - (ks - 1) / G) / (ks - 1)


def resid_kappa(y, f):
    X = np.c_[np.ones(len(y)), f]; r = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    d = r - r.mean(); return float((d ** 2).max() / (d ** 2).sum()), r


d = pd.read_csv(src); d = d[(d.task == 'CCRCC') & (d.encoder == 'uni_v2')]
fr = frontier(23, 7); rows = []
for gene, g in d.groupby('gene'):
    g = g.sort_values('donor'); y = g.mean_y.to_numpy(float); f = g.mean_f.to_numpy(float); don = g.donor.astype(str).to_numpy()
    k_all, r = resid_kappa(y, f)
    m = don != 'INT5'; k_int5, _ = resid_kappa(y[m], f[m])
    j = int(np.argmax((r - r.mean()) ** 2)); m2 = np.arange(len(y)) != j; k_orc, _ = resid_kappa(y[m2], f[m2])
    rows.append(dict(gene=gene, kappa_all=k_all, kappa_without_INT5=k_int5, kappa_without_top=k_orc, top_donor=don[j],
                     frontier_7_of_23=fr))
t = pd.DataFrame(rows); t.to_csv(f'{out}/i23_takeall_kappa.csv', index=False)
s = pd.DataFrame([dict(n_genes=len(t), frontier_7_of_23=fr, median_kappa_all=t.kappa_all.median(),
                       median_kappa_without_INT5=t.kappa_without_INT5.median(),
                       median_kappa_without_top=t.kappa_without_top.median(),
                       frac_inside_without_INT5=(t.kappa_without_INT5 < fr).mean(),
                       frac_inside_without_top=(t.kappa_without_top < fr).mean())])
s.to_csv(f'{out}/i23_takeall_summary.csv', index=False); print(s.T)
