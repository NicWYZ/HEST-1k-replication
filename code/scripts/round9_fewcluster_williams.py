"""Round 9, track fewcluster, step I3-4: Williams' (1961) estimator against round 5's (round 8 note, run 6.4.1).

Whole clusters labelled. For a population of G cluster values z_g with mean predictions f_g, and even n, each draw
takes a simple random sample L of n clusters and a random split into halves A and B.
  R5    : round 5's estimator c' Fbar + mean_L(z_g - lambda_(g) f_g), lambda_(g) the half-sample slope of the other
          half, clipped to [0, 1], zero when n < 6; equal to T1 - T2. Variance (1-f) s_e^2/n + (n/G)((lA-lB)/2)^2 s_f^2/n,
          t on n - 1 degrees of freedom (round 5's `textbook_t|fpc|lin|xf`).
  W     : Williams' estimator T1 - (1 - n/G) T2 = R5 + (n/G) T2, with the plain variance (1-f) s_e^2/n (W_plain) and with
          round 5's variance (W_r5var), t on n - 1.
  W_within: Williams' estimator with the residual variance pooled within halves (each half's residuals use one
          coefficient, so the variance does not depend on the level of f), (1-f) s_w^2/n, t on n - 2.
  FOLD  : fold-wise form; the unlabelled clusters are split at random between the folds as well,
          sum_j (N_j/G){lambda_(-j) Fbar_Uj + zbar_Sj - lambda_(-j) fbar_Sj}, variance
          sum_j (N_j/G)^2 (1 - n_j/N_j) s^2_{e,Sj}/n_j, t on n - 2.
  GLOB  : global least-squares slope on L (unclipped), variance (1-f) RSS/(n-2)/n, t on n - 2.
  FIX1  : fixed coefficient 1, variance (1-f) s^2_{z-f}/n, t on n - 1.
Outputs per population and n: bias, SD, RMSE, Monte Carlo SE of the bias, coverage and mean width at alpha = 0.10.
Modes: acs <i32_acs_states.csv> <outdir> ; hest <c0_cluster_summaries.csv.gz> <outdir>
"""
import sys, os, zlib
import numpy as np, pandas as pd
from scipy import stats

ALPHA = 0.10; R = 20000; NS = [4, 6, 8, 10, 12, 16]


def slope(z, f):
    fc = f - f.mean(-1, keepdims=True); zc = z - z.mean(-1, keepdims=True)
    v = (fc ** 2).sum(-1)
    return np.where(v > 0, (fc * zc).sum(-1) / np.where(v > 0, v, 1), 0.0)


def run_pop(z, f, rng):
    G = len(z); F = f.mean(); theta = z.mean(); out = []
    for n in NS:
        if n >= G:
            continue
        fr = n / G; h = n // 2
        idx = np.argsort(rng.random((R, G)), axis=1)
        L = idx[:, :n]; A, B = L[:, :h], L[:, h:]; U = idx[:, n:]
        zA, zB, fA, fB = z[A], z[B], f[A], f[B]
        zL, fL = z[L], f[L]
        if n >= 6:
            lA = np.clip(slope(zA, fA), 0, 1); lB = np.clip(slope(zB, fB), 0, 1)
        else:
            lA = lB = np.zeros(R)
        cp = (lA + lB) / 2
        r5 = cp * F + zL.mean(1) - (lB * fA.mean(1) + lA * fB.mean(1)) / 2
        T2 = 0.25 * (lB - lA) * (fA.mean(1) - fB.mean(1))
        w = r5 + fr * T2
        eA = zA - lB[:, None] * fA; eB = zB - lA[:, None] * fB
        se2 = np.concatenate([eA, eB], 1).var(1, ddof=1)
        sf2 = fL.var(1, ddof=1)
        v_plain = (1 - fr) * se2 / n
        v_r5 = v_plain + fr * ((lA - lB) / 2) ** 2 * sf2 / n
        t1 = stats.t.ppf(1 - ALPHA / 2, n - 1); t2 = stats.t.ppf(1 - ALPHA / 2, n - 2)
        # fold-wise: split the unlabelled clusters between folds
        nu = G - n; ua = (nu // 2 + (rng.random(R) < 0.5) * (nu % 2)).astype(int)
        col = np.arange(nu)[None, :]
        inA = col < ua[:, None]
        fU = f[U]
        sumA = np.where(inA, fU, 0).sum(1) + fA.sum(1); NA = ua + h
        sumB = np.where(~inA, fU, 0).sum(1) + fB.sum(1); NB = (nu - ua) + h
        # fold A uses the coefficient fitted on B (lambda_(-A) = lB), and vice versa
        tA = lB * sumA / NA + zA.mean(1) - lB * fA.mean(1)
        tB = lA * sumB / NB + zB.mean(1) - lA * fB.mean(1)
        fold = (NA / G) * tA + (NB / G) * tB
        vfold = (NA / G) ** 2 * (1 - h / NA) * eA.var(1, ddof=1) / h + (NB / G) ** 2 * (1 - h / NB) * eB.var(1, ddof=1) / h
        # global slope
        lg = slope(zL, fL)
        glob = zL.mean(1) - lg * (fL.mean(1) - F)
        res = (zL - zL.mean(1, keepdims=True)) - lg[:, None] * (fL - fL.mean(1, keepdims=True))
        vg = (1 - fr) * (res ** 2).sum(1) / (n - 2) / n
        fix = zL.mean(1) - (fL.mean(1) - F); vfix = (1 - fr) * (zL - fL).var(1, ddof=1) / n
        sw2 = ((h - 1) * eA.var(1, ddof=1) + (h - 1) * eB.var(1, ddof=1)) / (n - 2)
        v_within = (1 - fr) * sw2 / n
        forms = {'R5': (r5, v_r5, t1), 'W_within': (w, v_within, t2), 'W_plain': (w, v_plain, t1), 'W_r5var': (w, v_r5, t1),
                 'FOLD': (fold, vfold, t2), 'GLOB': (glob, vg, t2), 'FIX1': (fix, vfix, t1)}
        for k, (est, v, tq) in forms.items():
            err = est - theta; half = tq * np.sqrt(np.maximum(v, 0))
            out.append({'n': n, 'form': k, 'bias': err.mean(), 'sd': err.std(), 'rmse': np.sqrt((err ** 2).mean()),
                        'mcse_bias': err.std() / np.sqrt(R), 'coverage': float((np.abs(err) <= half).mean()),
                        'width': float(2 * half.mean())})
    return out


def main():
    mode, src, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261027); rows = []
    if mode == 'acs':
        s = pd.read_csv(src)
        a = s[s['lambda'] == 0.0].set_index('ST'); b = s[s['lambda'] == 1.0].set_index('ST')
        z = a.mean_e.to_numpy(); f = (a.mean_e - b.mean_e).to_numpy()
        for r in run_pop(z, f, rng):
            rows.append({'task': 'ACS_STATES', 'gene': 'log_income', **r})
        pd.DataFrame(rows).to_csv(os.path.join(out, 'i34_williams_acs.csv'), index=False)
    else:
        d = pd.read_csv(src)
        d = d[(d.encoder == 'uni_v2') & d.task.isin(['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM'])]
        for (task, gene), g in d.groupby(['task', 'gene']):
            if task == 'LUNG_XENIUM' and (zlib.crc32(gene.encode()) % 7 != 0):
                continue
            g = g.sort_values('donor')
            for r in run_pop(g.mean_y.to_numpy(float), g.mean_f.to_numpy(float), rng):
                rows.append({'task': task, 'gene': gene, **r})
        pd.DataFrame(rows).to_csv(os.path.join(out, 'i34_williams_hest.csv'), index=False)
    r = pd.DataFrame(rows)
    r['bias_z'] = r.bias / r.mcse_bias; r['bias_rel'] = r.bias.abs() / r.sd
    summ = r.groupby(['task', 'form', 'n']).agg(pops=('gene', 'size'), median_cov=('coverage', 'median'),
                                                 median_width=('width', 'median'), median_rmse=('rmse', 'median'),
                                                 frac_bias_z_lt3=('bias_z', lambda x: float((x.abs() < 3).mean())),
                                                 median_bias_rel=('bias_rel', 'median'),
                                                 q90_bias_rel=('bias_rel', lambda x: float(x.quantile(.9)))).reset_index()
    summ.to_csv(os.path.join(out, f'i34_williams_summary_{mode}.csv'), index=False)
    print(summ.to_string())


if __name__ == '__main__':
    main()
