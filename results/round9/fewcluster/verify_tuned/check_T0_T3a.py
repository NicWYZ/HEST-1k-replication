
import numpy as np, sys
sys.path.insert(0, ".")
from tuned_lib import *
rows = []
def add(**k): rows.append(k)

rng = np.random.default_rng(20261026)
# ---------- T0 : reduction + (E2) ----------
for (G, n) in [(8,4),(10,4),(10,5),(12,5)]:
    S = all_samples(G, n)
    worst_cov_diff = 0; worst_int = 0; worst_scale = 0; nt = 0
    for kind in ["normal","lognormal","normal_outlier"]:
        for rep in range(5):
            f = synth_f(G, kind, rng)
            z = rng.standard_normal(G) * rng.choice([1, 5]) + rng.integers(-3, 4)
            e = e_hat(z, f)
            a, c, b = rng.normal() * 3, rng.normal() * 3, rng.uniform(0.1, 10)
            zp = a + c * f + b * z
            # (E2): interval endpoints on every sample
            th, hw = interval(f, z, S, G); thp, hwp = interval(f, zp, S, G)
            worst_int = max(worst_int, np.abs(thp - (a + c * f.mean() + b * th)).max(),
                                       np.abs(hwp - b * hw).max())
            # T0: coverage mask depends only on e_hat and is scale-invariant
            for cc in [0.5, 1.0, 1.96, 3.0]:
                m1 = covered(f, z, S, cc)
                m2 = covered(f, e, S, cc, theta=0.0)
                m3 = covered(f, b * e, S, cc, theta=0.0)
                m4 = covered(f, zp, S, cc)       # z' has e_hat(z') = b e_hat(z)
                # exclude razor-edge samples (numerical ties) from the comparison
                diff = max((m1 != m2).sum(), (m2 != m3).sum(), (m1 != m4).sum())
                worst_cov_diff = max(worst_cov_diff, diff); nt += 1
            worst_scale = max(worst_scale, np.abs(e_hat(zp, f) - b * e).max())
    add(statement="T0", test="E2 interval transform: max |C(a+cf+bz)-(a+cFbar+bC(z))| over all samples/endpoints",
        G=G, n=n, value=worst_int, expected="~1e-12", passed=worst_int < 1e-8)
    add(statement="T0", test="covered-sample mask identical for z, e_hat(z), b e_hat(z), a+cf+bz (max #disagreeing samples)",
        G=G, n=n, value=worst_cov_diff, expected=0, passed=worst_cov_diff == 0)
    add(statement="T0", test="e_hat(a+cf+bz) = b e_hat(z) (max abs err)", G=G, n=n, value=worst_scale, expected="~1e-13", passed=worst_scale < 1e-9)

# ---------- T3(a): spike kappa formula ----------
for G in [6, 8, 10, 12, 15, 24, 40]:
    mx = 0; mismatch_max_at_g = 0
    for kind in ["normal","lognormal","normal_outlier"]:
        for rep in range(6):
            f = synth_f(G, kind, rng); H = hat_matrix(f)
            for g in range(G):
                z = np.zeros(G); z[g] = 1
                k1 = kappa(e_hat(z, f))
                hg = H[g].copy(); off = np.delete(hg, g)
                k2 = max((1 - H[g, g])**2, (off**2).max()) / (1 - H[g, g])
                mx = max(mx, abs(k1 - k2))
    add(statement="T3a", test="spike kappa(e_hat(1_g)) vs formula, max abs err over all g, 18 random f", G=G, n="",
        value=mx, expected="~1e-14", passed=mx < 1e-10)
# sum e^2 = 1-h_gg and mean e = 0
f = synth_f(12, "lognormal", rng); H = hat_matrix(f); z = np.zeros(12); z[3] = 1; e = e_hat(z, f)
add(statement="T3a", test="sum e^2 = 1-h_gg and sum e = 0 (abs err)", G=12, n="", value=abs(e@e-(1-H[3,3]))+abs(e.sum()), expected=0, passed=abs(e@e-(1-H[3,3]))+abs(e.sum())<1e-12)

import pandas as pd
pd.DataFrame(rows).to_csv("checks_T0_T3a.csv", index=False)
print(pd.DataFrame(rows).to_string())
