
import numpy as np, sys, pandas as pd
sys.path.insert(0, ".")
from tuned_lib import *
from beta_exact import *

def theta_zero_check(G, n, seed, kind):
    rng = np.random.default_rng(seed); f = synth_f(G, kind, rng)
    S = all_samples(G, n); Q = sample_constraints(f, S); fl = enumerate_flats(f, S, Q)
    NS = len(S); T = np.zeros((NS, G))                       # theta_hat_S as a linear functional of z
    fS = f[S]; fb = fS.mean(1); fc = fS - fb[:, None]; Sxx = (fc**2).sum(1); dF = f.mean() - fb
    for i in range(NS):
        T[i, S[i]] = np.full(n, 1 / n) + (dF[i] / Sxx[i]) * fc[i]
    bad = tot = 0
    for cnt, d, Bs in fl:
        if cnt == 0: continue
        R = np.einsum("sij,sjd->sid", Q, Bs[S]); cl = np.abs(R).reshape(NS, -1).max(1) < 1e-8
        th = T[cl] @ Bs
        tot += 1; bad += int((np.abs(th).max(1) < 1e-9).any())
    return tot, bad

rows = []
for G, n, sd in [(8, 4, 11), (10, 5, 21)]:
    for kind in ["normal", "lognormal", "normal_outlier"]:
        tot, bad = theta_zero_check(G, n, sd, kind)
        rows.append(dict(statement="T1prime/T2prime", test="for every flat with >=1 affine sample: is theta_hat_S identically 0 on the flat for some affine S? (count of such flats)",
                         G=G, n=n, f_kind=kind, result=bad, expected=0, flats_checked=tot, passed=(bad == 0)))
pd.DataFrame(rows).to_csv("checks_theta_generic.csv", index=False); print(pd.DataFrame(rows))
