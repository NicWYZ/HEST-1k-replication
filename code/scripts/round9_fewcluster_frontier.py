"""Round 9, track fewcluster: the exact max-share frontier (theorem note round09_fewcluster_frontier.md).

For each (G, n, alpha):
  kappa2(k)  = (1 - k/G)/k                          max-share of a two-point population with groups k <= G/2 and G-k
  pi(k)      = [C(G-k, n) + C(k, n)] / C(G, n)      share of n-subsets inside one level set of that population
  k_star     = smallest k <= G/2 with pi(k) <= alpha  (so kappa_star = kappa2(k_star) is the largest admissible kappa0)
  rest_bound = max over m < G/2 of [floor(G/m) C(m, n) + C(G mod m, n)] / C(G, n)
               (bound on subsets inside one level set when every level set is smaller than G/2)
  Lambda_star = sqrt(kappa_star (G - 1)): the same bound in residual standard deviations
Also the fraction of iid N(0,1) populations of size G with max-share <= kappa_star (20000 draws).
Output: results/round9/fewcluster/feasibility/s3_frontier_exact.csv
"""
import sys, math
import numpy as np, pandas as pd
from scipy.special import comb

OUT = sys.argv[1] if len(sys.argv) > 1 else 'results/round9/fewcluster/feasibility'
rng = np.random.default_rng(20261026)


def C(a, b):
    return comb(a, b, exact=True) if 0 <= b <= a else 0


rows = []
for G in (15, 24, 25, 51):
    Z = rng.standard_normal((20000, G))
    D = Z - Z.mean(1, keepdims=True)
    kap_gauss = (D ** 2).max(1) / (D ** 2).sum(1)
    for n in (4, 6, 8, 10, 12, 16):
        if n >= G:
            continue
        tot = C(G, n)
        for alpha in (0.05, 0.10):
            pi = {k: (C(G - k, n) + C(k, n)) / tot for k in range(1, G // 2 + 1)}
            pi_one = {k: C(G - k, n) / tot for k in range(1, G // 2 + 1)}
            ks = next((k for k in pi if pi[k] <= alpha), None)
            ks_one = next((k for k in pi_one if pi_one[k] <= alpha), None)
            rest = max((G // m) * C(m, n) + C(G % m, n) for m in range(1, (G + 1) // 2)) / tot
            kst = (1 - ks / G) / ks if ks else float('nan')
            rows.append(dict(G=G, n=n, alpha=alpha, k_star=ks, k_star_one_block=ks_one, kappa_star=kst,
                             pi_at_k_star=pi[ks] if ks else float('nan'),
                             pi_at_k_star_minus1=pi[ks - 1] if ks and ks > 1 else float('nan'),
                             rest_bound=rest, Lambda_star=math.sqrt(kst * (G - 1)),
                             frac_gauss_within=float(np.mean(kap_gauss <= kst)),
                             median_gauss_kappa=float(np.median(kap_gauss))))
df = pd.DataFrame(rows)
df.to_csv(f'{OUT}/s3_frontier_exact.csv', index=False)
print(df[df.alpha == 0.10][['G', 'n', 'k_star', 'k_star_one_block', 'kappa_star', 'Lambda_star', 'rest_bound',
                            'frac_gauss_within', 'median_gauss_kappa']].to_string(index=False))
