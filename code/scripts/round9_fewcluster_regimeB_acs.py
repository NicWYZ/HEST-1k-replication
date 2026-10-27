"""Round 9, track fewcluster, step I3-2: regime A against regime B on ACS PUMS 2018 by state (prediction R4).

Rebuilds round 4's person-level task (filter AGEP > 16, PINCP > 100, WKHP > 0, PWGTP >= 1; y = log PINCP;
cross-fitted HistGradientBoostingRegressor over five folds of states, the round 4 seeds), then for the fixed
coefficient lambda in {0, 1} computes
  regime A: cluster values z_g = state mean of y, residual e_g = z_g - lambda * state mean of f, Theorem 1's
            max-share kappa and the smallest n of 51 at which kappa lies strictly inside kappa2(k*(n) - 1);
  regime B: every state a stratum, m persons drawn in each, target the average of state means (W_h = 1/51),
            kappa_st = max_h v_h kappa_h and the stratified frontier of Theorem 3 for m = 2..30; the smallest m
            with kappa_st below the frontier's lower end (certified inside).
Labelling budget in persons for each regime. Outputs (aggregates only): i32_acs_states.csv, i32_acs_regimes.csv.
Usage: python round9_fewcluster_regimeB_acs.py ACSDIR OUTDIR
"""
import sys, os, zlib, math
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from round9_fewcluster_strat_frontier import frontier, kappa_st, thm1_frontier

acsdir, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
FEATS = ['AGEP', 'COW', 'SCHL', 'MAR', 'OCCP', 'POBP', 'RELP', 'WKHP', 'SEX', 'RAC1P']
df = pd.read_parquet(os.path.join(acsdir, 'acs_pums2018_all_columns.parquet'),
                     columns=['ST', 'PINCP', 'PWGTP'] + FEATS)
m = (df['AGEP'] > 16) & (df['PINCP'] > 100) & (df['WKHP'] > 0) & (df['PWGTP'] >= 1)
d = df[m].reset_index(drop=True)
y = np.log(d['PINCP'].to_numpy(np.float64)); X = d[FEATS].to_numpy(np.float64); st = d['ST'].to_numpy().astype(int)
fold_of_state = {int(s): zlib.crc32(str(int(s)).encode()) % 5 for s in np.unique(st)}
fold = np.array([fold_of_state[s] for s in st]); f = np.full(len(y), np.nan)
for k in range(5):
    te = fold == k
    mod = HistGradientBoostingRegressor(random_state=zlib.crc32(f'acs_pums2018_hgb_fold{k}'.encode()))
    mod.fit(X[~te], y[~te]); f[te] = mod.predict(X[te])
print('persons', len(y), 'R2', 1 - ((y - f) ** 2).sum() / ((y - y.mean()) ** 2).sum(), flush=True)

states = np.unique(st); G = len(states)
rows = []; reg = []
for lam in (0.0, 1.0):
    E = [y[st == s] - lam * f[st == s] for s in states]
    Ns = np.array([len(e) for e in E])
    zbar = np.array([e.mean() for e in E])
    for s, e in zip(states, E):
        dd = e - e.mean()
        rows.append({'lambda': lam, 'ST': int(s), 'N': len(e), 'mean_e': e.mean(), 'sd_e': e.std(ddof=1),
                     'kappa_h': (dd ** 2).max() / (dd ** 2).sum(), 'max_abs_z': np.abs(dd).max() / e.std(ddof=1)})
    # regime A
    dA = zbar - zbar.mean(); kA = float((dA ** 2).max() / (dA ** 2).sum())
    nA = next((n for n in range(2, G) if thm1_frontier(G, n) is not None and kA < thm1_frontier(G, n)), None)
    budgetA = None
    if nA is not None:   # persons in the nA largest and nA smallest states, as a range
        srt = np.sort(Ns); budgetA = (int(srt[:nA].sum()), int(srt[-nA:].sum()))
    reg.append({'lambda': lam, 'regime': 'A', 'kappa': kA, 'frontier_at_8': thm1_frontier(G, 8),
                'n_min': nA, 'budget_persons_min': budgetA[0] if budgetA else None,
                'budget_persons_max': budgetA[1] if budgetA else None})
    # regime B
    for mm in list(range(2, 13)) + [15, 20, 30]:
        kB, v = kappa_st(E, [1 / G] * G, [mm] * G)
        lo, up = frontier([(int(N), mm) for N in Ns], bins=3000)
        reg.append({'lambda': lam, 'regime': 'B', 'm': mm, 'kappa_st': kB, 'frontier_lo': lo, 'frontier_hi': up,
                    'inside': bool(kB < lo), 'beyond': bool(kB > up), 'max_v_h': float(v.max()),
                    'state_max': int(states[np.argmax(v * np.array([r['kappa_h'] for r in rows[-G:]]))]),
                    'budget_persons': G * mm})
        print(lam, mm, kB, lo, up, flush=True)
pd.DataFrame(rows).to_csv(os.path.join(out, 'i32_acs_states.csv'), index=False)
pd.DataFrame(reg).to_csv(os.path.join(out, 'i32_acs_regimes.csv'), index=False)
