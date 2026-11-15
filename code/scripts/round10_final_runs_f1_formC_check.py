"""Round 10, track final-runs, stage F1.1, part 4: form C in regime B with the coefficient fixed at 1.

Exact enumeration on toy two-cluster populations. Cluster 0 (M units) is sampled by every subset of m units (for
theta2, every stratified subset with floor(m/2) and ceil(m/2) per group, the larger share to the rarer group as in
round 5); cluster 1 is labelled in full. For each estimand (theta3 with weights of cluster mean zero, theta2 with two
groups, the ACS-style mean) and coefficient (fixed1, classical, crossfit is skipped because it needs two halves of
clusters), the check reports E(theta_hat) - theta (expected 0 for fixed1 and classical), E(V)/Var(theta_hat), and, at
coef classical, agreement with round 5's C_classical to 1e-12 (the identity of the inserted line at coefficient 0).
It also checks that the constant-within-cluster predictor gives fixed1 = classical (round 5's C_const identity).
Usage: round10_final_runs_f1_formC_check.py <outdir>
"""
import itertools, json, os, sys
import numpy as np, pandas as pd
import round5_ppi_twolevel as TL
import round10_final_runs_estimators as E


def population(kind, rng, M0=10, M1=6):
    M = M0 + M1; didx = np.r_[np.zeros(M0, int), np.ones(M1, int)]
    yhat = rng.normal(1.0, 0.7, (M, 1)); y = 0.8 * yhat + rng.gamma(1.5, 0.4, (M, 1))
    if kind == 'theta3':
        w = rng.normal(0, 1, M)
        for g in (0, 1):
            w[didx == g] -= w[didx == g].mean()
        group = None
    elif kind == 'theta2':
        group = np.r_[np.array([0] * 4 + [1] * 5 + [-1]), np.array([0] * 3 + [1] * 3)]
        w = np.zeros(M)                      # z_gi = w_gi y_gi with zbar_g = Ybar_N,g - Ybar_S,g
        for g in (0, 1):
            Mg = (didx == g).sum()
            for h, sgn in ((0, 1.0), (1, -1.0)):
                k = (didx == g) & (group == h); w[k] = sgn * Mg / k.sum()
    else:
        w = np.ones(M); group = None
    return y, yhat, w, didx, group


def subsets(kind, group0, M0, m):
    if kind != 'theta2':
        return [np.array(s) for s in itertools.combinations(range(M0), m)]
    g0 = np.flatnonzero(group0 == 0); g1 = np.flatnonzero(group0 == 1)
    rare, common = (g0, g1) if len(g0) <= len(g1) else (g1, g0)
    a = min(int(np.ceil(m / 2)), len(rare)); b = min(m - a, len(common))
    return [np.r_[list(s), list(t)] for s in itertools.combinations(rare, a) for t in itertools.combinations(common, b)]


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); rng = np.random.default_rng(20261109); rows = []
    for kind in ('theta3', 'theta2', 'mean'):
        y, yhat, w, didx, group = population(kind, rng)
        T = TL.prepare(y, yhat, w, didx, 2, kind, group=group)
        M0 = int((didx == 0).sum()); full1 = np.flatnonzero(didx == 1)
        for m in (4, 5, 6):
            subs = subsets(kind, T['group'][:M0], M0, m)
            for coef in ('fixed1', 'classical'):
                th, V, dmax = [], [], 0.0
                for s in subs:
                    sel = np.r_[s, full1]
                    o = E.regime_b_formC(T, sel, 'chk', coef)
                    th.append(o['theta'][0]); V.append(o['var'][0])
                    if coef == 'classical':
                        r = TL.estimate(T, np.ones(2, bool), sel, 'C_classical', 'chk', regime_b=True)
                        dmax = max(dmax, abs(r['theta'][0] - o['theta'][0]), abs(r['var'][0] - o['var'][0]))
                th, V = np.array(th), np.array(V)
                rows.append(dict(kind=kind, m=m, coef=coef, subsets=len(subs), bias=float(th.mean() - T['theta_full'][0]),
                                 V_ratio=float(V.mean() / th.var()) if th.var() > 0 else np.nan,
                                 d_vs_round5=dmax if coef == 'classical' else np.nan))
        # constant predictor within clusters: fixed1 equals classical
        yc = np.repeat(np.array([[0.3], [1.1]]), [M0, len(full1)], axis=0)
        Tc = TL.prepare(y, yc, w, didx, 2, kind, group=group); s = subsets(kind, Tc['group'][:M0], M0, 4)[0]
        a1 = E.regime_b_formC(Tc, np.r_[s, full1], 'chk', 'fixed1'); a0 = E.regime_b_formC(Tc, np.r_[s, full1], 'chk', 'classical')
        rows.append(dict(kind=kind, m=4, coef='const_identity', subsets=1,
                         bias=float(abs(a1['theta'][0] - a0['theta'][0])), V_ratio=float(abs(a1['var'][0] - a0['var'][0])),
                         d_vs_round5=np.nan))
    r = pd.DataFrame(rows); r.to_csv(os.path.join(out, 'f1_formC_check.csv'), index=False)
    unb = r[r.coef.isin(['fixed1', 'classical'])]
    res = dict(rows=len(r), max_abs_bias=float(unb.bias.abs().max()),
               max_d_vs_round5=float(r.d_vs_round5.max()),
               const_identity_max=float(r.loc[r.coef == 'const_identity', ['bias', 'V_ratio']].to_numpy().max()),
               V_ratio_range=[float(unb.V_ratio.min()), float(unb.V_ratio.max())])
    res['passed'] = bool(res['max_abs_bias'] < 1e-12 and res['max_d_vs_round5'] < 1e-12 and res['const_identity_max'] < 1e-12)
    json.dump(res, open(os.path.join(out, 'f1_formC_check_summary.json'), 'w'), indent=1)
    print(r.to_string()); print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
