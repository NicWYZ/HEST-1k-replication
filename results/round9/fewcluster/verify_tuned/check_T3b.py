
import numpy as np, sys, pandas as pd
sys.path.insert(0, ".")
from tuned_lib import *
rng = np.random.default_rng(99); rows = []
# (i) Where is the spike max attained?  scan outlier size L
for G in [12, 24]:
    base = rng.standard_normal(G - 1)
    for L in [2, 4, 8, 16, 32, 64, 128, 512]:
        f = np.append(base, L * base.std() + base.mean()); H = hat_matrix(f); g = G - 1
        e = e_hat(np.eye(G)[g], f); h = H[g, g]; off = np.abs(np.delete(H[g], g))
        rows.append(dict(statement="T3b", test="outlier scan", G=G, outlier_sd=L, h_gg=h, one_minus_h=1 - h, kappa_spike=kappa(e),
                         max_at_g=bool((1 - h)**2 >= off.max()**2), maxoff_sq_over_1mh=off.max()**2 / (1 - h),
                         lower_bound_h_over_Gm1=h / (G - 1), necessary_h_le_1_minus_1_over_G=bool(h <= 1 - 1 / G)))
# (ii) identity: sum_{j!=g} h_gj^2 = h(1-h); and 'max at g  =>  h<=1-1/G'
mx = 0; viol = 0; cnt = 0; att = 0
for G in [8, 12, 24]:
    for kind in ["normal", "lognormal", "normal_outlier"]:
        for rep in range(20):
            f = synth_f(G, kind, rng); H = hat_matrix(f)
            for g in range(G):
                off = np.delete(H[g], g); h = H[g, g]
                mx = max(mx, abs((off**2).sum() - h * (1 - h)))
                if (1 - h)**2 >= (off**2).max():
                    att += 1; cnt += 1
                    if h > 1 - 1 / G + 1e-12: viol += 1
                else: cnt += 1
rows.append(dict(statement="T3b", test="identity sum_{j!=g}h_gj^2=h_gg(1-h_gg) [max abs err]; 'max attained at g' implies h_gg<=1-1/G (violations / cases where attained)",
                 value=mx, violations=viol, n_attained=att, n_total=cnt, passed=(mx < 1e-12 and viol == 0)))
# (iii) T1' for a spike by exact enumeration
for (G, n) in [(10, 4), (12, 5)]:
    S = all_samples(G, n)
    for kind in ["normal", "normal_outlier"]:
        f = synth_f(G, kind, rng); H = hat_matrix(f)
        ks = np.array([kappa(e_hat(np.eye(G)[g], f)) for g in range(G)])
        g = int(np.argmin(ks)); z = np.zeros(G); z[g] = 1; kap0 = ks[g] * 1.02
        covs = []
        for eps in [1e-4, 1e-6]:
            for t in range(5):
                x = rng.standard_normal(G); ze = z + eps * x
                assert kappa(e_hat(ze, f)) < kap0
                covs.append(coverage(f, ze, S, 100.0))
        rows.append(dict(statement="T3b", test="spike z*=1_g (g=argmin spike kappa) tuned coverage at z*+eps x, c=100 vs 1-n/G", G=G, n=n, f_kind=kind,
                         g=g, h_gg=H[g, g], kappa_spike=ks[g], kappa0=kap0, max_cov=max(covs), one_minus_P_W=1 - (1 - n / G), passed=max(covs) <= n / G + 1e-12 + 0 or abs(max(covs) - n / G) < 1e-12))
        print(rows[-1], flush=True)
df = pd.DataFrame(rows); df.to_csv("checks_T3b.csv", index=False)
print(df[df.test == "outlier scan"].drop(columns=["statement", "test"]).round(5).to_string())
print(df.tail(5).to_string())
