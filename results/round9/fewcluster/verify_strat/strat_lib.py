"""Exact finite-population machinery for the stratified (K_st) verification. Independent code."""
import itertools, math
from math import comb
import numpy as np

def subsets_idx(N, n):
    return np.array(list(itertools.combinations(range(N), n)), dtype=np.int64)

class Design:
    """strata h: (N_h, n_h, W_h). Enumerates all prod C(N_h,n_h) samples (uniform)."""
    def __init__(self, Ns, ns, Ws):
        self.Ns, self.ns, self.Ws = list(Ns), list(ns), np.array(Ws, float)
        self.H = len(Ns)
        self.idx = [subsets_idx(N, n) if n < N else None for N, n in zip(Ns, ns)]
        self.nsamp = [len(ix) if ix is not None else 1 for ix in self.idx]
    # --- population-level quantities
    def V_h(self, e):
        out = []
        for h in range(self.H):
            N, n, W = self.Ns[h], self.ns[h], self.Ws[h]
            eh = np.asarray(e[h], float); d = eh - eh.mean()
            out.append(W**2 * (1 - n / N) * (d @ d) / ((N - 1) * n))
        return np.array(out)
    def kappa_h(self, eh):
        eh = np.asarray(eh, float); d = (eh - eh.mean())**2
        s = d.sum()
        return d.max() / s if s > 0 else 0.0
    def kappa_st(self, e):
        """by definition: max_{h,i} c_hi, c_hi = W^2 (1-f) d^2 / (n (N-1) V)"""
        V = self.V_h(e).sum()
        if V <= 0: return None
        best = 0.0
        for h in range(self.H):
            N, n, W = self.Ns[h], self.ns[h], self.Ws[h]
            eh = np.asarray(e[h], float); d2 = (eh - eh.mean())**2
            best = max(best, (W**2 * (1 - n / N) * d2 / (n * (N - 1) * V)).max())
        return best
    def kappa_st_identity(self, e):
        Vh = self.V_h(e); V = Vh.sum()
        if V <= 0: return None
        return max((Vh[h] / V) * self.kappa_h(e[h]) if Vh[h] > 0 else 0.0 for h in range(self.H))
    # --- sampling distribution (exact)
    def dist(self, e):
        """returns arrays over all samples: diff = T - theta, SE (exact), uniform probs."""
        diff = np.zeros(1); se2 = np.zeros(1)
        for h in range(self.H):
            N, n, W = self.Ns[h], self.ns[h], self.Ws[h]
            eh = np.asarray(e[h], float)
            if n == N:
                dh = np.zeros(1); sh = np.zeros(1)
            else:
                vals = eh[self.idx[h]]                      # (S,n)
                m = vals.mean(1)
                dh = W * (m - eh.mean())
                s2 = ((vals - m[:, None])**2).sum(1) / (n - 1)
                sh = W**2 * (1 - n / N) * s2 / n
            diff = (diff[:, None] + dh[None, :]).ravel()
            se2 = (se2[:, None] + sh[None, :]).ravel()
        return diff, np.sqrt(se2)
    def p_se0(self, e):
        """exact P(every non-take-all stratum sample is constant) via product of per-stratum probabilities"""
        p = 1.0
        for h in range(self.H):
            N, n = self.Ns[h], self.ns[h]
            if n == N: continue
            vals, cnt = np.unique(np.round(np.asarray(e[h], float), 12), return_counts=True)
            p *= sum(comb(int(c), n) for c in cnt) / comb(N, n)
        return p
    def fail_prob(self, e, c, diff_se=None):
        diff, se = diff_se if diff_se is not None else self.dist(e)
        # cover iff |diff|<=c*se  (point when se==0 -> covers iff diff==0 up to tol)
        scale = max(1e-300, np.abs(diff).max())
        cover = np.where(se > 0, np.abs(diff) <= c * se, np.abs(diff) <= 1e-12 * scale)
        return 1 - cover.mean()
    def c_needed(self, e, alpha, diff_se=None):
        """smallest c with P(|T-theta|>c SE)<=alpha (inf if the SE=0 & diff!=0 mass exceeds alpha)"""
        diff, se = diff_se if diff_se is not None else self.dist(e)
        scale = max(1e-300, np.abs(diff).max())
        bad0 = (se == 0) & (np.abs(diff) > 1e-12 * scale)
        S = len(diff)
        if bad0.sum() / S > alpha + 1e-12: return math.inf
        pos = se > 0
        r = np.where(pos, np.abs(diff) / np.where(pos, se, 1), 0.0)
        r = np.sort(r[pos])[::-1]               # decreasing
        allowed = int(math.floor((alpha + 1e-12) * S)) - int(bad0.sum())   # how many failing samples allowed
        if allowed >= len(r): return 0.0
        return float(r[allowed])                # fail set = those strictly > c ; choose c=r[allowed]
        
# ---------- levels / knapsack ----------
def pi_k(N, n, k):  return (comb(N - k, n) + comb(k, n)) / comb(N, n)
def a_k(N, k):      return k * N / (N - k)
def R_h(N, n):
    best = 0.0
    for m in range(1, N):
        if 2 * m < N:
            best = max(best, ((N // m) * comb(m, n) + comb(N % m, n)) / comb(N, n))
    return best
def levels(N, n, use_R):
    L = [(pi_k(N, n, k), a_k(N, k), f'k={k}') for k in range(1, N // 2 + 1)]
    if use_R: L.append((R_h(N, n), float(N), 'R'))
    return L
def cap_knapsack(strata, alpha, use_R):
    """strata: list of (N,n) with n<N. Exhaustive over (exclude | level) per stratum; product > alpha (strict),
    nonempty A. returns (max total capacity, argmax choices) or (-inf,None)."""
    opts = [[None] + levels(N, n, use_R) for (N, n) in strata]
    best, arg = -math.inf, None
    for ch in itertools.product(*opts):
        used = [c for c in ch if c is not None]
        if not used: continue
        pr = 1.0
        for c in used: pr *= c[0]
        if pr > alpha:
            cap = sum(c[1] for c in used)
            if cap > best: best, arg = cap, ch
    return best, arg
def cap_given_p(strata, p0, use_R=True, strict=False):
    """max total capacity subject to product >= p0"""
    opts = [[None] + levels(N, n, use_R) for (N, n) in strata]
    best = -math.inf
    for ch in itertools.product(*opts):
        used = [c for c in ch if c is not None]
        if not used: continue
        pr = 1.0
        for c in used: pr *= c[0]
        if pr >= p0 - 1e-12: best = max(best, sum(c[1] for c in used))
    return best
