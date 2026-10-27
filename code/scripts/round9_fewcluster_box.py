"""Round 9, track fewcluster, step I3-2: regime A against regime B under the box class of Theorem 3.

Box class: every residual within Lambda0 within-stratum standard deviations of its stratum mean
(kappa_h (N_h - 1) <= Lambda0^2) and every stratum at most v0 of the design variance of the stratified estimator.
Its frontier needs ceil(1/v0) strata degenerate at once, so the worst probability of an all-constant sample is the
product of the ceil(1/v0) largest per-stratum factors, each the two-point factor pi_h(k_min,h) with k_min,h the smallest
minority size whose two-point population has Lambda <= Lambda0 (lower = upper bound when the Proposition 3 level R_h
is smaller, which is checked and reported). A population is inside when that worst product is <= alpha at its own
(Lambda0, v0) = (max_h Lambda_h, max_h v_h). Regime A uses Theorem 1 on the cluster means.

Modes
  acs_states <i32_acs_states.csv> <outdir>  (local; ACS aggregates by state)
  hest <repo_root_on_longleaf> <outdir>     (Longleaf; per-spot parquets, writes gene-level results only)
"""
import sys, os, math, functools
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from round9_fewcluster_strat_frontier import log_pi, log_R as _log_R, thm1_frontier


@functools.lru_cache(maxsize=None)
def log_R(N, n):
    return _log_R(N, n)

ALPHA = 0.10
M_GRID = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100]


def k_min(N, lam0):
    # kappa2(k)(N-1) = (N-k)(N-1)/(N k) <= lam0^2  <=>  k >= N(N-1)/(N lam0^2 + N - 1)
    return max(1, math.ceil(N * (N - 1) / (N * lam0 ** 2 + N - 1) - 1e-12))


def box_worst(Ns, sds, m, lam0, alpha=ALPHA):
    """Worst all-constant probability over the box class at this population's v0. Returns (low, up, v0, s)."""
    Ns = np.asarray(Ns); sds = np.asarray(sds, float)
    mm = np.minimum(m, Ns)
    Vh = sds ** 2 * (1 - mm / Ns) / mm          # W_h = 1/G common, dropped
    v = Vh / Vh.sum(); v0 = float(v.max()); s = math.ceil(1 / v0 - 1e-12)
    prob = mm < Ns
    lo, up = [], []
    for N, mh, p in zip(Ns, mm, prob):
        if not p:
            continue
        k = min(k_min(int(N), lam0), int(N) // 2)
        l2 = float(log_pi(int(N), int(mh), [k])[0])
        lr = log_R(int(N), int(mh)) if lam0 ** 2 >= (N - 1) / N else -np.inf
        lo.append(l2); up.append(max(l2, lr))
    lo = np.sort(lo)[::-1]; up = np.sort(up)[::-1]
    if s > len(lo):
        return 0.0, 0.0, v0, s
    return math.exp(lo[:s].sum()), math.exp(up[:s].sum()), v0, s


def regime_A(zbar, G):
    d = zbar - zbar.mean(); kA = float((d ** 2).max() / (d ** 2).sum())
    nA = next((n for n in range(2, G) if (fr := thm1_frontier(G, n)) is not None and kA < fr), None)
    return kA, nA


def analyse(groups, label):
    """groups: list of residual arrays per cluster (one lambda). Returns one row."""
    Ns = np.array([len(e) for e in groups]); sds = np.array([e.std(ddof=1) for e in groups])
    lam_h = np.array([np.abs(e - e.mean()).max() / e.std(ddof=1) for e in groups])
    lam0 = float(lam_h.max()); G = len(groups)
    kA, nA = regime_A(np.array([e.mean() for e in groups]), G)
    row = {**label, 'G': G, 'N_median': float(np.median(Ns)), 'Lambda0': lam0, 'Lambda_h_median': float(np.median(lam_h)),
           'kappa_A': kA, 'n_min_A': nA, 'frontier_A_mid': thm1_frontier(G, 8 if G > 15 else 6)}
    mB = None; mB_up = None
    for m in M_GRID:
        lo, up, v0, s = box_worst(Ns, sds, m, lam0)
        if mB is None and up <= ALPHA:
            mB = m
        if mB_up is None and lo <= ALPHA:
            mB_up = m
        if m in (5, 10, 20):
            row[f'worst_m{m}'] = up; row[f'v0_m{m}'] = v0; row[f's_m{m}'] = s
    row['m_min_B'] = mB              # certified inside (upper bound <= alpha)
    row['m_min_B_twopoint'] = mB_up  # two-point bound only
    return row


def main():
    mode, src, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    rows = []
    if mode == 'acs_states':
        s = pd.read_csv(src)
        for lam, d in s.groupby('lambda'):
            # reconstruct what analyse needs from aggregates
            Ns = d.N.to_numpy(); sds = d.sd_e.to_numpy(); lam_h = np.sqrt(d.kappa_h * (d.N - 1)).to_numpy()
            lam0 = float(lam_h.max()); G = len(d)
            kA, nA = regime_A(d.mean_e.to_numpy(), G)
            row = {'task': 'ACS_STATES', 'lambda': lam, 'G': G, 'N_median': float(np.median(Ns)), 'Lambda0': lam0,
                   'Lambda_h_median': float(np.median(lam_h)), 'kappa_A': kA, 'n_min_A': nA,
                   'frontier_A_mid': thm1_frontier(G, 8)}
            mB = mB2 = None
            for m in M_GRID:
                lo, up, v0, s_ = box_worst(Ns, sds, m, lam0)
                if mB is None and up <= ALPHA: mB = m
                if mB2 is None and lo <= ALPHA: mB2 = m
                if m in (5, 10, 20):
                    row[f'worst_m{m}'] = up; row[f'v0_m{m}'] = v0; row[f's_m{m}'] = s_
            row['m_min_B'] = mB; row['m_min_B_twopoint'] = mB2
            rows.append(row)
        pd.DataFrame(rows).to_csv(os.path.join(out, 'i32_acs_box.csv'), index=False)
        print(pd.DataFrame(rows).T)
        return
    if mode == 'hest':
        PQ = {"CCRCC": "results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet",
              "INDIANA_KIDNEY": "results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet",
              "LUNG_XENIUM": "results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet"}
        for task, pq in PQ.items():
            df = pd.read_parquet(os.path.join(src, pq))
            genes = [c[3:] for c in df.columns if c.startswith('y__')]
            don = df.donor_id.astype(str).to_numpy(); ud = np.unique(don)
            idx = [np.where(don == u)[0] for u in ud]
            for g in genes:
                y = df['y__' + g].to_numpy(float); f = df['f__' + g].to_numpy(float)
                for lam in (0.0, 1.0):
                    e = y - lam * f
                    groups = [e[i] for i in idx]
                    if min(np.std(x) for x in groups) == 0:
                        rows.append({'task': task, 'gene': g, 'lambda': lam, 'note': 'constant donor'}); continue
                    rows.append(analyse(groups, {'task': task, 'gene': g, 'lambda': lam}))
            print(task, len(genes), flush=True)
        r = pd.DataFrame(rows); r.to_csv(os.path.join(out, 'i32_hest_box_genes.csv'), index=False)
        summ = r.groupby(['task', 'lambda']).agg(n_genes=('gene', 'size'), Lambda0_median=('Lambda0', 'median'),
                                                 m_min_B_median=('m_min_B', 'median'),
                                                 frac_B_le10=('m_min_B', lambda x: float((x <= 10).mean())),
                                                 frac_B_le30=('m_min_B', lambda x: float((x <= 30).mean())),
                                                 frac_B_none=('m_min_B', lambda x: float(x.isna().mean())),
                                                 n_min_A_median=('n_min_A', 'median'),
                                                 frac_A_none=('n_min_A', lambda x: float(x.isna().mean()))).reset_index()
        summ.to_csv(os.path.join(out, 'i32_hest_box_summary.csv'), index=False)
        print(summ.to_string())


if __name__ == '__main__':
    main()
