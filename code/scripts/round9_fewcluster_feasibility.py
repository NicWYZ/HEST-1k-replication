"""Round 9, track fewcluster, step S3 (local part).

1. The boundary kappa*(n, G, alpha): k* is the smallest k with C(G-k, n)/C(G, n) <= alpha,
   kappa* = (1 - k*/G)/k*, the max-share of a two-point population with k* atypical clusters.
2. Exact coverage of the finite-population t interval
       zbar_S +- t_{n-1, 1-alpha/2} sqrt((1 - n/G) s^2 / n)
   under simple random sampling without replacement, over populations taking two or three
   distinct values, and the worst case as a function of the max-share bound kappa0.
3. A direct search over general populations (G = 15, n = 6, every subset enumerated) to see
   whether few-valued populations attain the worst case.
4. ACS by state: max-share of state means and of state contributions of log income (raw).

Predictions: results/round9/fewcluster/feasibility/predictions_before_run.md.
Outputs: results/round9/fewcluster/feasibility/*.csv
"""
import itertools, json, math, os, sys
import numpy as np
from scipy import stats
from scipy.special import comb

OUT = sys.argv[1] if len(sys.argv) > 1 else 'results/round9/fewcluster/feasibility'
os.makedirs(OUT, exist_ok=True)


def kappa(z):
    d = np.asarray(z, float) - np.mean(z)
    ss = np.sum(d ** 2)
    return float(np.max(d ** 2) / ss) if ss > 0 else 0.0


def boundary(n, G, alpha):
    for k in range(1, G + 1):
        if comb(G - k, n, exact=True) / comb(G, n, exact=True) <= alpha:
            return k, (1 - k / G) / k
    return None, None


# ---------- 1. boundary grid
rows = []
for G in (15, 24, 25, 51):
    for n in (4, 6, 8, 10, 12, 16):
        if n >= G:
            continue
        for alpha in (0.05, 0.10):
            k, ks = boundary(n, G, alpha)
            miss = comb(G - k, n, exact=True) / comb(G, n, exact=True)
            rows.append(dict(G=G, n=n, alpha=alpha, k_star=k, kappa_star=ks, miss_prob_at_k_star=miss,
                             lemma_bound=max(0.0, (1 - alpha - n / G) / (1 - n / G))))
import pandas as pd
bd = pd.DataFrame(rows)
bd.to_csv(f'{OUT}/s3_boundary_grid.csv', index=False)


# ---------- 2. exact coverage over few-valued populations
def coverage_counts(counts, vals, n, alpha):
    """Exact coverage of the fpc t interval for a population with counts[i] clusters at vals[i]."""
    counts = np.asarray(counts, int); vals = np.asarray(vals, float)
    G = counts.sum(); theta = np.dot(counts, vals) / G
    tq = stats.t.ppf(1 - alpha / 2, n - 1)
    tot = comb(G, n, exact=True); cov = 0.0
    m = len(counts)
    for js in itertools.product(*[range(min(c, n) + 1) for c in counts[:-1]]):
        jl = n - sum(js)
        if jl < 0 or jl > counts[-1]:
            continue
        j = np.array(list(js) + [jl])
        p = np.prod([comb(int(c), int(x), exact=True) for c, x in zip(counts, j)]) / tot
        if p == 0:
            continue
        zbar = np.dot(j, vals) / n
        s2 = np.dot(j, (vals - zbar) ** 2) / (n - 1)
        hw = tq * math.sqrt((1 - n / G) * s2 / n)
        if abs(zbar - theta) <= hw + 1e-12:
            cov += p
    return cov


def pop_from(counts, vals):
    return np.repeat(np.asarray(vals, float), np.asarray(counts, int))


few_rows = []
vgrid = np.concatenate([-np.geomspace(0.02, 50, 60)[::-1], np.geomspace(0.02, 50, 60)])
for (G, n) in ((15, 6), (24, 8), (25, 8), (51, 8)):
    alpha = 0.10
    # two-point: k clusters at 1, G-k at 0
    for k in range(1, G):
        c = coverage_counts([G - k, k], [0.0, 1.0], n, alpha)
        few_rows.append(dict(G=G, n=n, alpha=alpha, family='two_point', m0=G - k, m1=k, m2=0, v=np.nan,
                             kappa=kappa(pop_from([G - k, k], [0, 1])), coverage=c))
    # three-point: m0 at 0, m1 at 1, m2 at v (vectorised over v)
    tq = stats.t.ppf(1 - alpha / 2, n - 1); tot = comb(G, n, exact=True)
    vv = vgrid[np.abs(vgrid - 1) > 1e-9]
    for m1 in range(1, G - 1):
        for m2 in range(1, G - m1):
            m0 = G - m1 - m2
            if m0 < 1:
                continue
            J = [(j1, j2) for j1 in range(min(m1, n) + 1) for j2 in range(min(m2, n - j1) + 1) if n - j1 - j2 <= m0]
            J = np.array(J, float)
            P = np.array([comb(m0, n - int(a) - int(b), exact=True) * comb(m1, int(a), exact=True) * comb(m2, int(b), exact=True)
                          for a, b in J]) / tot
            j1 = J[:, :1]; j2 = J[:, 1:]; j0 = n - j1 - j2
            V = vv[None, :]
            zbar = (j1 + j2 * V) / n
            s2 = (j0 * zbar ** 2 + j1 * (1 - zbar) ** 2 + j2 * (V - zbar) ** 2) / (n - 1)
            theta = (m1 + m2 * V) / G
            cov = (P[:, None] * (np.abs(zbar - theta) <= tq * np.sqrt((1 - n / G) * s2 / n) + 1e-12)).sum(0)
            mean = (m1 + m2 * vv) / G
            dev0, dev1, dev2 = mean ** 2, (1 - mean) ** 2, (vv - mean) ** 2
            ss = m0 * dev0 + m1 * dev1 + m2 * dev2
            kap = np.maximum(np.maximum(dev0, dev1), dev2) / ss
            for v, c, kk in zip(vv, cov, kap):
                few_rows.append(dict(G=G, n=n, alpha=alpha, family='three_point', m0=m0, m1=m1, m2=m2, v=v,
                                     kappa=float(kk), coverage=float(c)))
few = pd.DataFrame(few_rows)
few.to_csv(f'{OUT}/s3_fewvalued_coverage.csv.gz', index=False)

# worst case as a function of kappa0
wc_rows = []
for (G, n), sub in few.groupby(['G', 'n']):
    k, ks = boundary(n, G, 0.10)
    for kap0 in sorted(set(np.round(np.r_[np.linspace(0.02, 0.9, 45), ks], 6))):
        s = sub[sub.kappa <= kap0 + 1e-12]
        if len(s) == 0:
            continue
        w = s.loc[s.coverage.idxmin()]
        wc_rows.append(dict(G=G, n=n, kappa0=kap0, is_kappa_star=bool(abs(kap0 - ks) < 1e-6), kappa_star=ks,
                            worst_coverage=w.coverage, worst_family=w.family, m0=w.m0, m1=w.m1, m2=w.m2, v=w.v,
                            worst_kappa=w.kappa))
wc = pd.DataFrame(wc_rows)
wc.to_csv(f'{OUT}/s3_worstcase_by_kappa0.csv', index=False)


# ---------- 3. direct search over general populations, G = 15, n = 6 (all 5005 subsets)
def coverage_general(z, subsets, n, alpha):
    G = len(z); theta = z.mean(); tq = stats.t.ppf(1 - alpha / 2, n - 1)
    zs = z[subsets]
    zbar = zs.mean(1); s2 = zs.var(1, ddof=1)
    hw = tq * np.sqrt((1 - n / G) * s2 / n)
    return float(np.mean(np.abs(zbar - theta) <= hw + 1e-12))


rng = np.random.default_rng(20261026)
G, n = 15, 6
subsets = np.array(list(itertools.combinations(range(G), n)))
search_rows = []
for kap0 in (0.10, 0.15, 0.20, 0.30, 0.45):
    best = None
    for start in range(40):
        # start from a random skewed population, rescaled into the class if needed
        z = rng.standard_normal(G) * np.exp(rng.uniform(0, 2) * rng.standard_normal(G))
        if kappa(z) > kap0:
            # shrink the most extreme value toward the mean until inside
            for _ in range(200):
                i = np.argmax(np.abs(z - z.mean())); z[i] = z.mean() + 0.9 * (z[i] - z.mean())
                if kappa(z) <= kap0:
                    break
        if kappa(z) > kap0:
            continue
        cur = coverage_general(z, subsets, n, 0.10); step = 0.5
        for it in range(600):
            z2 = z.copy(); i = rng.integers(G)
            z2[i] += step * z.std() * rng.standard_normal()
            if kappa(z2) > kap0:
                continue
            c2 = coverage_general(z2, subsets, n, 0.10)
            if c2 <= cur:
                z, cur = z2, c2
            if it % 150 == 149:
                step *= 0.6
        if best is None or cur < best[0]:
            best = (cur, z.copy())
    zb = best[1]
    ndistinct = len(np.unique(np.round((zb - zb.mean()) / zb.std(), 3)))
    search_rows.append(dict(G=G, n=n, kappa0=kap0, search_worst_coverage=best[0], kappa_found=kappa(zb),
                            n_distinct_values_3dp=ndistinct,
                            fewvalued_worst=float(few[(few.G == G) & (few.n == n) & (few.kappa <= kap0 + 1e-12)].coverage.min()),
                            pop_standardized=json.dumps(list(np.round(np.sort((zb - zb.mean()) / zb.std()), 3)))))
pd.DataFrame(search_rows).to_csv(f'{OUT}/s3_general_search_G15_n6.csv', index=False)

# ---------- 4. ACS by state (raw, no predictions)
ACS = '/Users/nicolaszhang/hest-1k/acs_pums2018/acs_pums2018_all_columns.parquet'
if os.path.exists(ACS):
    import pyarrow.parquet as pq
    d = pq.read_table(ACS, columns=['ST', 'AGEP', 'PINCP', 'WKHP', 'PWGTP']).to_pandas()
    m = (d['AGEP'] > 16) & (d['PINCP'] > 100) & (d['WKHP'] > 0) & (d['PWGTP'] >= 1)
    d = d[m]; d['y'] = np.log(d['PINCP'].astype(float))
    g = d.groupby('ST')['y'].agg(['mean', 'size'])
    Gs = len(g); N = g['size'].sum()
    contrib = Gs * g['size'] * g['mean'] / N   # cluster contributions to the person-level mean
    acs = []
    for name, z in (('state_mean', g['mean'].to_numpy()), ('state_contribution', contrib.to_numpy())):
        dz = z - z.mean(); i = int(np.argmax(dz ** 2))
        acs.append(dict(target=name, G=Gs, kappa=kappa(z), argmax_ST=int(g.index[i]),
                        skew=float(stats.skew(z)), z_of_max=float(dz[i] / z.std(ddof=1))))
    pd.DataFrame(acs).to_csv(f'{OUT}/s3_acs_states_kappa.csv', index=False)
print('done')
