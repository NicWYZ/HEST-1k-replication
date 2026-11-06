"""Shared helpers for verifying the finite-population frontier statements."""
import itertools, math
from math import comb
import numpy as np

def C(a, b):
    return comb(a, b) if 0 <= b <= a else 0

def kappa2(G, k):
    return (1 - k / G) / k

def pi_k(G, n, k):
    return (C(G - k, n) + C(k, n)) / C(G, n)

def kappa(e):
    d = np.asarray(e, float); d = d - d.mean()
    ss = (d ** 2).sum()
    if ss <= 1e-300:
        return np.nan
    return (d ** 2).max() / ss

_samp_cache = {}
def samples(G, n):
    key = (G, n)
    if key not in _samp_cache:
        _samp_cache[key] = np.array(list(itertools.combinations(range(G), n)), dtype=np.int32)
    return _samp_cache[key]

def miss_mask(e, c, G, n, idx=None):
    """Boolean array over all C(G,n) samples: True if fpc-t interval
    ebar_S +- c*sqrt((1-n/G) s^2/n) misses ebar (point interval when s=0)."""
    if idx is None:
        idx = samples(G, n)
    e = np.asarray(e, float)
    eS = e[idx]
    base = eS[:, :1]
    dev = eS - base                        # exact zeros when e constant on S
    m = dev.mean(1)
    var = ((dev - m[:, None]) ** 2).sum(1) / (n - 1)
    se = np.sqrt((1 - n / G) * var / n)
    gap = np.abs(base[:, 0] + m - e.mean())
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(var == 0, gap > 0, gap > c * se)

def const_count(e, G, n, idx=None):
    if idx is None:
        idx = samples(G, n)
    eS = np.asarray(e, float)[idx]
    return int((eS == eS[:, :1]).all(1).sum())

def partitions(G, maxpart=None):
    if maxpart is None: maxpart = G
    if G == 0:
        yield (); return
    for m in range(min(G, maxpart), 0, -1):
        for rest in partitions(G - m, m):
            yield (m,) + rest

def min_kappa_partition(part):
    """min of kappa over non-constant e that are constant on the blocks of `part`
    (exact: vertex enumeration of max sum m_i w_i^2 over {w in [0,1]^r, sum s_i m_i w_i = 0}).
    Returns (kappa_min, e_star) with e_star a population vector."""
    from collections import Counter
    cnt = Counter(part)
    sizes = sorted(cnt)
    best = (-1.0, None)
    # states per size class: (p, q, z) = #plus, #minus, #zero blocks (full weight on p,q)
    def options(q):
        return [(a, b, q - a - b) for a in range(q + 1) for b in range(q + 1 - a)]
    for combo in itertools.product(*[options(cnt[m]) for m in sizes]):
        P = sum(m * c[0] for m, c in zip(sizes, combo))
        N = sum(m * c[1] for m, c in zip(sizes, combo))
        full = sum(m * (c[0] + c[1]) for m, c in zip(sizes, combo))
        D = P - N
        if D == 0:
            if full > best[0] + 1e-12 and full > 0:
                best = (full, (combo, None, 0.0))
        else:
            # fractional zero block of size m_j with opposite sign, weight |D|/m_j <= 1
            for m, c in zip(sizes, combo):
                if c[2] > 0 and abs(D) <= m:
                    w = abs(D) / m
                    val = full + m * w * w
                    if val > best[0] + 1e-12:
                        best = (val, (combo, m, w))
    V, (combo, mfrac, w) = best
    # build e
    e = []
    used_frac = False
    for m, c in zip(sizes, combo):
        for _ in range(c[0]): e += [1.0] * m
        for _ in range(c[1]): e += [-1.0] * m
        for _ in range(c[2]):
            if mfrac == m and not used_frac:
                used_frac = True
                D = sum(mm * cc[0] for mm, cc in zip(sizes, combo)) - sum(mm * cc[1] for mm, cc in zip(sizes, combo))
                e += [(-np.sign(D)) * w] * m
            else:
                e += [0.0] * m
    e = np.array(e)
    return 1.0 / V, e
