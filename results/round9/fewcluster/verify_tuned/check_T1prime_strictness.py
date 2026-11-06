
import numpy as np, sys, pandas as pd
sys.path.insert(0, ".")
from tuned_lib import *
from beta_exact import *
rng = np.random.default_rng(11); f = synth_f(8, "normal", rng)   # same f as the G=8 T2' run
S = all_samples(8, 4); Q = sample_constraints(f, S)
fl = enumerate_flats(f, S, Q); out, _, _ = beta_curve(f, 4, fl, S, Q)
cands = [(k, v, c) for c, d, k, v in out if c == 5]
kmin, v, c = min(cands, key=lambda t: t[0])
v = v / np.linalg.norm(v); n_tied = int((np.abs(np.abs(v) - np.abs(v).max()) < 1e-9).sum())
B0 = base_basis(f); ok = 0; N = 4000
for _ in range(N):
    u = B0 @ rng.standard_normal(B0.shape[1])
    if kappa(v + 1e-6 * u) <= kmin * (1 + 1e-12): ok += 1
pd.DataFrame([dict(statement="T1prime", test="strictness: z*=min-kappa element of a count-5 flat, kappa0=kappa(z*) exactly; fraction of random directions x with kappa(e_hat(z*+eps x))<=kappa0",
                   G=8, n=4, kappa_zstar=kmin, n_tied_max_coords=n_tied, fraction_in_K=ok / N, passed=(ok / N) < 0.5)]).to_csv("checks_T1prime_strictness.csv", index=False)
print(kmin, n_tied, ok / N)
