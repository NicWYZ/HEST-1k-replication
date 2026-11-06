
"""beta_exact.py -- exact enumeration of collinearity flats of e (perp to 1,f) and exact min-kappa on each flat.
beta_OLS(kappa0) = max_{flats V' with min_{e in V'} kappa(e) <= kappa0, dim V'>=1} (#samples affine on all of V') / C(G,n)
"""
import numpy as np, itertools, sys
from math import comb
sys.path.insert(0, ".")
from tuned_lib import *

def sample_constraints(f, S):
    """Q[s] : (n-2) x n orthonormal basis of the orthogonal complement of span(1, f_S) in R^n."""
    NS, n = S.shape
    Q = np.empty((NS, n - 2, n))
    for i in range(NS):
        X = np.column_stack([np.ones(n), f[S[i]]])
        u, _, _ = np.linalg.svd(X, full_matrices=True)
        Q[i] = u[:, 2:].T
    return Q

def base_basis(f):
    G = len(f); X = np.column_stack([np.ones(G), f])
    u, _, _ = np.linalg.svd(X, full_matrices=True)
    return u[:, 2:]                      # G x (G-2), orthonormal basis of {e perp 1, f}

def kappa_min_exact(Bs, tol=1e-10):
    """min over e in span(Bs) of max e_g^2 / sum e^2, by vertex enumeration of {|v_g|<=1} in span(Bs)."""
    G, d = Bs.shape
    if d == 1:
        v = Bs[:, 0]; return (v**2).max() / (v @ v), v / np.abs(v).max()
    combos = np.array(list(itertools.combinations(range(G), d)))
    A = Bs[combos]                                             # m x d x d
    dets = np.abs(np.linalg.det(A)); A = A[dets > 1e-9]
    rows = combos[dets > 1e-9]
    signs = np.array(list(itertools.product([-1.0, 1.0], repeat=d)))   # 2^d x d
    best = -1; bestv = None
    for j in range(0, len(A), 4000):
        Aj = A[j:j + 4000]
        y = np.linalg.solve(Aj[:, None, :, :], signs[None, :, :, None])[..., 0]   # m x 2^d x d
        v = y @ Bs.T                                                                # m x 2^d x G
        feas = np.abs(v).max(-1) <= 1 + 1e-8
        val = (v**2).sum(-1); val[~feas] = -1
        i = np.unravel_index(np.argmax(val), val.shape)
        if val[i] > best: best, bestv = val[i], v[i]
    return 1.0 / best, bestv

def closure_count(Bs, Q, S, tol=1e-8):
    R = np.einsum("sij,sjd->sid", Q, Bs[S])      # NS x (n-2) x d  (Bs[S] : NS x n x d)
    return (np.abs(R).reshape(len(S), -1).max(1) < tol)

def enumerate_flats(f, S, Q, max_nodes=10**7, verbose=False, starts=None):
    """DFS over the lattice of flats; returns list of (closure_bitkey, count, d, Bs)."""
    G = len(f); NS, n = S.shape
    seen = {}
    stack = [base_basis(f)] if starts is None else list(starts)
    flats = []
    while stack:
        Bs = stack.pop()
        d = Bs.shape[1]
        R = np.einsum("sij,sjd->sid", Q, Bs[S])           # NS x (n-2) x d
        cl = np.abs(R).reshape(NS, -1).max(1) < 1e-8
        flats.append((int(cl.sum()), d, Bs))
        if d <= 1: continue
        cand = np.where(~cl)[0]
        U, sv, Vt = np.linalg.svd(R[cand], full_matrices=True)    # Vt: (m, d, d)
        for ii, s_i in enumerate(cand):
            rank = int((sv[ii] > 1e-8).sum())
            if rank == 0: continue
            dn = d - rank
            if dn < 1: continue
            newB = Bs @ Vt[ii][rank:].T                    # G x dn
            P = newB @ newB.T
            key = np.round(P, 7).tobytes()
            if key in seen: continue
            seen[key] = 1
            stack.append(newB)
            if len(seen) > max_nodes: raise RuntimeError("too many nodes")
        if verbose and len(flats) % 2000 == 0: print(len(flats), len(stack), flush=True)
    return flats

def beta_curve(f, n, flats=None, S=None, Q=None):
    """for every flat compute exact kappa_min; return DataFrame-like arrays (count, d, kappa_min, v)"""
    G = len(f)
    if S is None: S = all_samples(G, n)
    if Q is None: Q = sample_constraints(f, S)
    if flats is None: flats = enumerate_flats(f, S, Q)
    out = []
    # unique flats only matter by (count, kappa_min): evaluate kappa_min for every flat with d>=1
    for cnt, d, Bs in flats:
        k, v = kappa_min_exact(Bs)
        out.append((cnt, d, k, v))
    return out, S, Q
