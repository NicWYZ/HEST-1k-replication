#!/usr/bin/env python
"""Round 4, conformal track, stage C1: this track's GHCP and HCP against the released GHCP code.

docs/round4_conf_plan.md section 4, C1 known method 5. The released implementation
(github.com/soham-penn/hierarchical_CP, commit recorded in PROVENANCE) is imported unmodified
from --ghcp-code. On random inputs with a fixed zero global predictor (so that the paper's merger
eq. (3) and this track's residual recentring coincide), for random K, group sizes, o, alpha and
eta, the check compares:

  hcp    round4_conf_sim.hcp_q against methods.baseline_hcp.compute_hcp_interval_radius;
  ghcp   round4_conf_sim.ghcp_q with pool_rule='code', the released code's donor and
         n_glob = |S_train| of that pool, against the half-width and centre of
         methods.donor_hcp.compute_donor_hcp_randomized_interval with
         create_mu_method_pretrained_global(zero model, c = 1);
  pool   the paper's restricted pool size (eq. 8) against the code's, recorded as a difference
         and not as a failure.

Group sizes are distinct within a draw so that no cutoff tie arises (the two implementations
break ties with different random streams, which is allowed and is not what is being checked).
"""
import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_sim as S  # noqa: E402
import round4_conf_io as IO  # noqa: E402


class Zero:
    def predict(self, X):
        return np.zeros(np.asarray(X).reshape(len(X), -1).shape[0])


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--ghcp-code", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--n", type=int, default=400)
    a = p.parse_args(argv)
    sys.path.insert(0, a.ghcp_code)
    from methods.baseline_hcp import compute_hcp_interval_radius
    from methods.donor_hcp import compute_donor_hcp_randomized_interval, _select_s_tilde_with_tie_randomization
    from methods.mu_methods import create_mu_method_pretrained_global
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for t in range(a.n):
        rng = np.random.default_rng(S.crc(f"C1codepath|{t}"))
        K = int(rng.choice([5, 7, 10, 12, 20]))
        N = rng.choice(np.arange(8, 400), size=K, replace=False)
        o = int(rng.choice([0, 1, 2, 5, 10, 20]))
        alpha = float(rng.choice([0.05, 0.1, 0.2]))
        eta = float(rng.choice([0.0, 0.25, 0.5]))
        sig_a = float(rng.choice([0.0, 1.0]))
        a_k = rng.normal(0, sig_a, K + 1)
        cal = [a_k[k] + rng.standard_normal(N[k]) for k in range(K)]
        test = a_k[K] + rng.standard_normal(max(o + 1, 25))
        # hcp
        q_mine = S.hcp_q([np.abs(x) for x in cal], alpha)
        q_ref = float(compute_hcp_interval_radius([np.abs(x) for x in cal], alpha))
        rows.append(dict(check="hcp", t=t, K=K, o=o, alpha=alpha, eta=eta, mine=q_mine, ref=q_ref,
                         diff=abs(q_mine - q_ref) if np.isfinite(q_ref) else float(q_mine != q_ref)))
        # ghcp, code pool
        pool_code = S.restricted_pool(N, o, eta, rng, rule="code") if eta > 0 else np.where(N > o)[0]
        ref_pool = _select_s_tilde_with_tie_randomization(N=N, o_observed=o, alpha_selection=eta)
        pool_paper = S.restricted_pool(N, o, eta, rng, rule="paper")
        rows.append(dict(check="pool_size_code_minus_paper", t=t, K=K, o=o, alpha=alpha, eta=eta,
                         mine=len(pool_paper), ref=len(ref_pool), diff=len(ref_pool) - len(pool_paper)))
        same_pool = set(pool_code.tolist()) == set(np.asarray(ref_pool).tolist())
        rows.append(dict(check="pool_code_rule_equals_released", t=t, K=K, o=o, alpha=alpha,
                         eta=eta, mine=len(pool_code), ref=len(ref_pool), diff=float(not same_pool)))
        if len(ref_pool) == 0 or not same_pool:
            continue
        seed = int(S.crc(f"C1codepath|donor|{t}"))
        donor = int(np.random.default_rng(seed).choice(ref_pool))
        n_glob = K - len(ref_pool)
        U = np.zeros((K, 1))
        Z = [[{"X": np.array([0.0]), "Y": float(y)} for y in x] for x in cal]
        Zt = [{"X": np.array([0.0]), "Y": float(y)} for y in test]
        mu = create_mu_method_pretrained_global(Zero(), tau=1, c=1.0)
        out = compute_donor_hcp_randomized_interval(U, Z, np.zeros((1, 1)), Zt, o, alpha, eta, mu,
                                                   random_seed=seed)
        lo, hi = out["interval"]
        q_ref = (hi - lo) / 2 if np.isfinite(hi) else math.inf
        c_ref = (hi + lo) / 2 if np.isfinite(hi) else float("nan")
        q_m, c_m = S.ghcp_q(cal, test, o, alpha, rng, adapt=True, eta=eta, n_glob=n_glob,
                            pool_rule="code", J0=donor) if eta > 0 else S.ghcp_q(
            cal, test, o, alpha, rng, adapt=True, eta=0.0, n_glob=n_glob, J0=donor)
        d = abs(q_m - q_ref) if np.isfinite(q_ref) and np.isfinite(q_m) else float(np.isfinite(q_m) != np.isfinite(q_ref))
        rows.append(dict(check="ghcp_halfwidth", t=t, K=K, o=o, alpha=alpha, eta=eta, mine=q_m,
                         ref=q_ref, diff=d))
        if np.isfinite(q_ref):
            rows.append(dict(check="ghcp_centre", t=t, K=K, o=o, alpha=alpha, eta=eta, mine=c_m,
                             ref=c_ref, diff=abs(c_m - c_ref)))
    d = pd.DataFrame(rows)
    d.to_csv(f"{a.out}/c1_codepath_rows.csv", index=False)
    summ = (d.groupby("check").agg(n=("diff", "size"), max_diff=("diff", "max"),
                                   n_nonzero=("diff", lambda x: int((x > 1e-10).sum())))
            .reset_index())
    summ.to_csv(f"{a.out}/c1_codepath.csv", index=False)
    print(summ.to_string(index=False))
    IO.write_provenance(a.out, "C1", __file__, dict(stage="C1 codepath", n=a.n,
                                                    ghcp_code=a.ghcp_code))
    ok = all(summ[summ.check.isin(["hcp", "ghcp_halfwidth", "ghcp_centre",
                                   "pool_code_rule_equals_released"])].max_diff <= 1e-10)
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
