
"""tuned_lib.py -- exact enumeration tools for the tuned-PPI finite-population checks."""
import itertools, numpy as np
from math import comb

def all_samples(G, n):
    return np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(G), n)),
                       dtype=np.int16).reshape(-1, n).astype(np.int64)

def pi_k(G, n, k):
    return (comb(G-k, n) + comb(k, n)) / comb(G, n)

def hat_matrix(f):
    X = np.column_stack([np.ones(len(f)), f])
    return X @ np.linalg.solve(X.T @ X, X.T)

def e_hat(z, f):
    return z - hat_matrix(f) @ z

def kappa(e):
    e = np.asarray(e, float); ec = e - e.mean(); s = ec @ ec
    return np.inf if s == 0 else (ec**2).max() / s

def sample_stats(f, z, S):
    """per-sample tuned quantities. returns theta_hat, RSS, Sxx"""
    n = S.shape[1]
    fS, zS = f[S], z[S]
    fb, zb = fS.mean(1), zS.mean(1)
    fc = fS - fb[:, None]
    Sxx = (fc**2).sum(1)
    lam = (fc * (zS - zb[:, None])).sum(1) / Sxx
    th = zb + lam * (f.mean() - fb)
    res = zS - zb[:, None] - lam[:, None] * fc
    return th, (res**2).sum(1), Sxx

def interval(f, z, S, G):
    n = S.shape[1]
    th, rss, _ = sample_stats(f, z, S)
    s2 = rss / (n - 2)
    return th, np.sqrt((1 - n / G) * s2 / n)   # centre, half-width per unit c

def covered(f, z, S, c, theta=None, zero_tol=0.0):
    G = len(f)
    th, hw = interval(f, z, S, G)
    theta = z.mean() if theta is None else theta
    return np.abs(th - theta) <= c * hw + zero_tol

def coverage(f, z, S, c, **kw):
    return covered(f, z, S, c, **kw).mean()

def affine_mask(f, z, S, rel=1e-9):
    """samples on which z_S is exactly affine in f_S (RSS tiny relative to scale)"""
    th, rss, _ = sample_stats(f, z, S)
    sc = max(np.abs(z).max(), 1e-300)
    return rss <= (rel * sc) ** 2

def synth_f(G, kind, rng):
    if kind == "normal":
        return rng.standard_normal(G)
    if kind == "lognormal":
        return rng.lognormal(0, 1, G)
    if kind == "normal_outlier":
        x = rng.standard_normal(G); x[np.argmax(x)] = x.mean() + 4 * x.std(); return x
    raise ValueError(kind)
