"""Round 9, track fewcluster, step I3-1: the frontier for stratified designs (Theorem 3).

Setting. Strata h = 1..H with N_h units (clusters in regime A, units within a cluster in regime B), n_h drawn by
simple random sampling without replacement, independently across strata. Fixed coefficient, so the data are residuals
e. Target theta = sum_h W_h mean(e_h). Stratified estimator sum_h W_h mean(e_{S_h}), design variance
V = sum_h W_h^2 (1 - n_h/N_h) S_h^2 / n_h. The share of unit (h, i) is W_h^2 (1 - n_h/N_h)(e_hi - mean e_h)^2 /
(n_h (N_h - 1) V), and kappa_st is the largest share, equal to max_h v_h kappa_h with v_h = V_h / V.

Frontier. A stratum with a two-point population of minority size k contributes a factor pi_h(k) to the
probability that every sampled stratum is constant and a capacity a_h(k) = 1 / kappa2_h(k) = k N_h / (N_h - k).
Impossibility when some choice of strata and levels has product of pi above alpha and total capacity above
1 / kappa0; possibility when no choice has total capacity reaching 1 / kappa0 with product above alpha. So the
frontier is 1 / Cap*, Cap* = max total capacity subject to sum of -log pi < log(1/alpha) (multiple-choice knapsack).
Cap_low uses two-point levels only, costs rounded up (every choice counted is feasible). Cap_up adds the level of
populations without a level set of half the stratum (factor R_h, capacity N_h; Proposition 3 of the frontier note),
costs rounded down. Hence 1/Cap_up <= kappa*_st <= 1/Cap_low.

Usage: imported by the checks and the regime-B scripts; `python round9_fewcluster_strat_frontier.py check <outdir>`
runs the predictions R1 to R3 and the brute-force checks.
"""
import sys, math, itertools, os
import numpy as np
from scipy.special import gammaln

ALPHA = 0.10


def lC(a, b):
    a = np.asarray(a, float); b = float(b)
    out = np.full(a.shape, -np.inf)
    ok = a >= b
    out[ok] = gammaln(a[ok] + 1) - gammaln(b + 1) - gammaln(a[ok] - b + 1)
    return out


def log_pi(N, n, k):
    """log of [C(N-k,n) + C(k,n)] / C(N,n) for an array k."""
    k = np.asarray(k, float)
    return np.logaddexp(lC(N - k, n), lC(k, n)) - lC(np.array([N]), n)[0]


def log_R(N, n):
    """Proposition 3's bound for populations whose largest level set is below N/2."""
    ms = np.arange(max(n, 1), int(math.ceil(N / 2)))
    if len(ms) == 0:
        return -np.inf
    q = N // ms; r = N % ms
    val = np.logaddexp(np.log(q) + lC(ms, n), lC(r, n)) - lC(np.array([N]), n)[0]
    return float(val.max())


def levels(N, n, upper=False):
    """(cost, capacity) pairs of one stratum. Take-all strata (n = N) have none."""
    if n >= N:
        return np.zeros(0), np.zeros(0)
    k = np.arange(1, N // 2 + 1)
    cost = -log_pi(N, n, k)
    cap = k * N / (N - k)
    if upper:
        lr = log_R(N, n)
        if np.isfinite(lr):
            cost = np.r_[cost, -lr]; cap = np.r_[cap, float(N)]
    return np.maximum(cost, 0.0), cap


def cap_star(strata, alpha=ALPHA, bins=4000, mode='low'):
    """Max total capacity with sum of costs < log(1/alpha). strata: list of (N_h, n_h)."""
    L = math.log(1 / alpha); d = L / bins
    dp = np.full(bins, -np.inf); dp[0] = 0.0      # dp[b]: best capacity with rounded cost exactly b (then cummax)
    cache = {}
    for (N, n) in strata:
        key = (N, n)
        if key not in cache:
            cost, cap = levels(N, n, upper=(mode == 'up'))
            fin = np.isfinite(cost)
            cost, cap = cost[fin], cap[fin]
            b = np.ceil(cost / d - 1e-12).astype(int) if mode == 'low' else np.floor(cost / d + 1e-12).astype(int)
            keep = b <= bins - 1
            b, cap = b[keep], cap[keep]
            best = {}
            for bi, ci in zip(b, cap):
                if ci > best.get(bi, -1):
                    best[bi] = ci
            cache[key] = sorted(best.items())
        new = dp.copy()
        for bi, ci in cache[key]:
            cand = dp[:bins - bi] + ci
            np.maximum(new[bi:], cand, out=new[bi:])
        dp = new
    return float(np.max(dp))


def best_config(strata, alpha=ALPHA, bins=4000):
    """Two-point levels only, costs rounded up: returns Cap_low and the minority size k_h per stratum (0 = off)."""
    L = math.log(1 / alpha); d = L / bins
    dp = np.full(bins, -np.inf); dp[0] = 0.0; choice = []
    for (N, n) in strata:
        cost, cap = levels(N, n)
        fin = np.isfinite(cost); ks = np.arange(1, N // 2 + 1)[fin] if n < N else np.zeros(0, int)
        cost, cap = cost[fin], cap[fin]
        b = np.ceil(cost / d - 1e-12).astype(int); keep = b <= bins - 1
        new = dp.copy(); arg = np.zeros(bins, int)
        for bi, ci, ki in zip(b[keep], cap[keep], ks[keep]):
            cand = np.r_[np.full(bi, -np.inf), dp[:bins - bi] + ci]
            better = cand > new
            new[better] = cand[better]; arg[better] = ki
        choice.append((arg.copy(), dict(zip(ks[keep], b[keep]))))
        dp = new
    bstar = int(np.argmax(dp)); cap_tot = float(dp[bstar]); ks_out = []
    for h in range(len(strata) - 1, -1, -1):
        arg, bk = choice[h]; k = int(arg[bstar]); ks_out.append(k)
        if k > 0:
            bstar -= int(bk[k])
    return cap_tot, ks_out[::-1]


def frontier(strata, alpha=ALPHA, bins=4000):
    lo, up = cap_star(strata, alpha, bins, 'low'), cap_star(strata, alpha, bins, 'up')
    return 1 / up, 1 / lo           # kappa*_st lies in [1/Cap_up, 1/Cap_low]


def kappa_st(E, W, n):
    """E: list of 1-d residual arrays per stratum; returns kappa_st and v_h."""
    Vh, kh = [], []
    for e, w, m in zip(E, W, n):
        N = len(e); d = e - e.mean(); ss = (d ** 2).sum()
        Vh.append(w ** 2 * (1 - m / N) * ss / (N - 1) / m if m < N else 0.0)
        kh.append((d ** 2).max() / ss if ss > 0 else 0.0)
    Vh = np.array(Vh); V = Vh.sum(); v = Vh / V
    return float((v * np.array(kh)).max()), v


# ---------------------------------------------------------------- checks
def thm1_frontier(G, n, alpha=ALPHA):
    for k in range(1, G // 2 + 1):
        if math.exp(log_pi(G, n, [k])[0]) <= alpha:
            return float('inf') if k == 1 else (1 - (k - 1) / G) / (k - 1)
    return None


def enum_strat(E, W, n, c):
    """Exact miss probability and P(SE = 0) of the stratified t-type interval with critical value c."""
    per = []
    for e, m in zip(E, n):
        N = len(e); rows = []
        for S in itertools.combinations(range(N), m):
            x = e[list(S)]
            rows.append((x.mean(), x.var(ddof=1) if m > 1 else 0.0))
        per.append(np.array(rows))
    theta = sum(w * e.mean() for e, w in zip(E, W))
    grids = np.meshgrid(*[np.arange(len(p)) for p in per], indexing='ij')
    est = sum(W[h] * per[h][grids[h], 0] for h in range(len(E)))
    var = sum(W[h] ** 2 * (1 - n[h] / len(E[h])) * per[h][grids[h], 1] / n[h] for h in range(len(E)))
    se = np.sqrt(np.maximum(var, 0))
    tol = 1e-12 * (1 + np.abs(est).max())
    miss = np.abs(est - theta) > c * se + tol
    zero = se <= 1e-12 * (1 + np.sqrt(np.abs(var).max()))
    return float(miss.mean()), float(zero.mean())


def run_checks(out):
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261027)
    lines = []
    # R1: one stratum equals Theorem 1 on the interval-1 grid
    bad = 0; cells = 0
    for G in (14, 15, 24, 25, 51):
        for n in (4, 6, 8, 12, 16):
            if n >= G:
                continue
            t1 = thm1_frontier(G, n)
            if t1 is None or not np.isfinite(t1):
                continue
            lo, up = frontier([(G, n)], bins=20000)
            cells += 1
            # kappa*_st is in [lo, up]; Theorem 1 gives exactly t1 when R is small
            if not (lo <= t1 * (1 + 1e-3) and t1 <= up * (1 + 1e-3)):
                bad += 1; lines.append(f'R1 mismatch G={G} n={n} thm1={t1:.5f} bracket=({lo:.5f},{up:.5f})')
    lines.append(f'R1: {cells} cells, {bad} outside the bracket')
    # R2: two strata of 12 with 4 each
    lo, up = frontier([(12, 4), (12, 4)], bins=20000)
    lines.append(f'R2: two strata 12/4: kappa*_st in [{lo:.4f}, {up:.4f}]; unstratified 8 of 24 = {thm1_frontier(24, 8):.4f}')
    # R3: regime B synthetic
    G, N = 24, 2000
    pops = [rng.standard_normal((G, N)) for _ in range(21)]
    for m in (2, 3, 4, 5, 6, 8):
        lo, up = frontier([(N, m)] * G, bins=4000)
        ks = [kappa_st(list(P), [1 / G] * G, [m] * G)[0] for P in pops]
        med = float(np.median(ks))
        lines.append(f'R3: m={m}: kappa*_st in [{lo:.3e}, {up:.3e}], median kappa_st of normal pops {med:.3e}, '
                     f'inside (below lower end) {np.mean(np.array(ks) < lo):.2f}')
    # Brute force 1: populations with P(SE=0) > alpha must have kappa_st >= 1/Cap_up (possibility side)
    designs = [((6, 3), (5, 2)), ((7, 3), (6, 3)), ((6, 2), (6, 2)), ((8, 4), (5, 3)), ((6, 3), (6, 3), (5, 2))]
    viol = 0; tested = 0
    for des in designs:
        Ns = [d[0] for d in des]; ns = [d[1] for d in des]; W = [N_ / sum(Ns) for N_ in Ns]
        for a in (0.05, 0.10, 0.20, 0.30):
            lo, up = frontier(list(des), alpha=a, bins=20000)
            for _ in range(400):
                E = []
                for N_ in Ns:
                    nv = rng.integers(1, 4)
                    vals = rng.standard_normal(nv) * rng.choice([1e-3, 1, 1, 10])
                    E.append(vals[rng.integers(0, nv, N_)] + 1e-9 * 0)
                if all(np.ptp(e) == 0 for e in E):
                    continue
                k_, _ = kappa_st(E, W, ns)
                _, z = enum_strat(E, W, ns, 1.0)
                tested += 1
                if z > a + 1e-12 and k_ < lo * (1 - 1e-9):
                    viol += 1
    lines.append(f'BF1: {tested} few-valued populations, {viol} with P(SE=0) > alpha inside the possibility region')
    # Brute force 2: the two-point construction defeats a large critical value just above 1/Cap_low
    rows = []
    for des in designs:
        Ns = [d[0] for d in des]; ns = [d[1] for d in des]; W = [N_ / sum(Ns) for N_ in Ns]
        lo, up = frontier(list(des), alpha=ALPHA, bins=20000)
        rows.append((des, lo, up))
    for des, lo, up in rows:
        lines.append(f'design {des}: kappa*_st in [{lo:.4f}, {up:.4f}]')
    # Brute force 2: build the optimal two-point configuration, scale strata so v_h is proportional to capacity,
    # and check that the interval with critical value 1e8 misses with probability above alpha at kappa_st = 1/Cap_low
    for des in designs + [((12, 4), (12, 4)), ((10, 3), (10, 3), (10, 3))]:
        Ns = [d_[0] for d_ in des]; ns = [d_[1] for d_ in des]; W = [N_ / sum(Ns) for N_ in Ns]
        cap, ks = best_config(list(des), bins=20000)
        E = []; caps = []
        for (N_, m), k in zip(des, ks):
            caps.append(k * N_ / (N_ - k) if k else 0.0)
        for (N_, m), k, cp, w in zip(des, ks, caps, W):
            if k == 0:
                E.append(np.zeros(N_)); continue
            # V_h = w^2 (1 - m/N) S^2 / m with S^2 = k (N - k) / (N (N - 1)) a^2; set V_h proportional to cp
            s2unit = w ** 2 * (1 - m / N_) * k * (N_ - k) / (N_ * (N_ - 1)) / m
            a = math.sqrt(cp / s2unit) * (1 + 0.01 * rng.random())
            e = np.zeros(N_); e[:k] = a; E.append(e)
        k_, v = kappa_st(E, W, ns)
        miss, zero = enum_strat(E, W, ns, 1e8)
        prod = math.prod(math.exp(log_pi(N_, m, [k])[0]) for (N_, m), k in zip(des, ks) if k)
        lines.append(f'BF2 {des}: ks={ks} kappa_st={k_:.4f} (1/Cap_low={1/cap:.4f}) miss at c=1e8 {miss:.4f}, '
                     f'P(SE=0) {zero:.4f}, product of pi {prod:.4f}')
    open(os.path.join(out, 'i31_checks.txt'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    if sys.argv[1] == 'check':
        run_checks(sys.argv[2])
