
import numpy as np, sys, time, itertools, pandas as pd
from math import comb
sys.path.insert(0, ".")
from tuned_lib import *

# ---------- (1) internal consistency of the attached table ----------
P = "/Users/nicolaszhang/.claude-science/orgs/c42040b3-6d87-451b-9b93-c94218d0c812/artifacts/proj_cdb12919c7d7/c6a4feec-f243-4336-b7d6-6340757fb76a/ve25d9733_i22_tuned_frontier.csv"
df = pd.read_csv(P); rows = []
def kstar(G, n, a):  return min(k for k in range(1, G) if pi_k(G, n, k) <= a)
for i, r in df.iterrows():
    G, n, a = int(r.G), int(r.n), r.alpha
    ks = kstar(G, n, a); ks1 = kstar(G, n - 1, a)
    fx = 1 / (ks - 1) - 1 / G; fx1 = 1 / (ks1 - 1) - 1 / G
    kf = int(r.k_found); Bn = len(str(r.B2_found).split())
    kmax_valid = ks - 1
    rows.append(dict(statement="NUMBERS", test="table row consistency", G=G, n=n, f_kind=r.f_kind,
        k_star_ok=(ks == r.k_star), fixed_eq_1_over_kstar_minus_1_minus_1_over_G=abs(fx - r.fixed_frontier) < 1e-6,
        fixed_n_minus_1_formula_ok=abs(fx1 - r.fixed_frontier_n_minus_1) < 1e-6,
        pi_at_k_found_ok=abs(pi_k(G, n, kf) - r.pi_at_k_found) < 1e-6, pi_gt_alpha=r.pi_at_k_found > a,
        len_B2_eq_k_found=(Bn == kf), k_found_eq_kstar_minus_1=(kf == kmax_valid),
        tuned_lt_fixed=r.tuned_frontier_upper < r.fixed_frontier, tuned_upper=r.tuned_frontier_upper, fixed=r.fixed_frontier))
tab = pd.DataFrame(rows)
tab.columns = [c.replace("_formula_1_over_(k*-1)_minus_1_over_G_ok", "_fixed_formula_ok") if False else c for c in tab.columns]
tab.to_csv("checks_numbers_table_consistency.csv", index=False)
print(tab.drop(columns=["statement","test"]).to_string())
