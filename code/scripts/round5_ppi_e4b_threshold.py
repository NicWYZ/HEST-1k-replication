"""Round 5 PPI, E4b acceptance 1: the change in D2's threshold between E4 and E4b.

E4 (round5_ppi_e4_selection.py) took D2's threshold as the p_a quantile of the Mahalanobis distance
over its pool of 200 draws x 2,000 candidates; E4b (round5_ppi_e4b_rejective.py) over 2,000 draws x
the first 500 candidates. Neither wrote E4's value, so this recomputes both, per task, arm,
estimand, n_L, balance variable (own, pcF2, pcE2, perm; perm_cluster is new in E4b) and p_a, with the
same candidate seeds and distance code, and writes the median over genes of each threshold and of
their ratio: e4b_threshold__<vtag>__<arm>.csv. Nothing is estimated.
"""
import argparse
import os

import numpy as np
import pandas as pd

import round4_ppi_q2_masking as Q2
import round5_ppi_e4b_rejective as RJ
from round5_ppi_e2_regimeB import load_arm, ACS
from round5_ppi_e4_selection import pcs, donor_arrays, embeddings


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--perm-parquet", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--nl-grid", default="4,6,8,12")
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    data = load_arm(a.parquet, a.arm, a.vtag)
    pdata = load_arm(a.perm_parquet, "permuted", a.vtag)
    donors = np.asarray(data["donors"]); Gall = len(donors)
    enc = "resnet50" if a.arm == "permuted" else a.arm
    emb = None if a.vtag in ACS else embeddings(a.root, a.vtag, enc, donors)
    rows = []
    for est in Q2.ESTS:
        _, fbar_all, ok = donor_arrays(data, est)
        _, fperm_all, _ = donor_arrays(pdata, est)
        vid = np.flatnonzero(ok)
        fbar, fperm = fbar_all[vid], fperm_all[vid]
        bal = {"own": fbar[:, :, None], "perm": fperm[:, :, None], "pcF2": pcs(fbar, 2)[:, None, :]}
        if emb is not None and np.isfinite(emb[vid]).all():
            bal["pcE2"] = pcs(emb[vid], 2)[:, None, :]
        for nL in map(int, a.nl_grid.split(",")):
            if nL > Gall - 2:
                continue
            pools = {}
            for name, nd, nc in (("E4", 200, 2000), ("E4b", 2000, 500)):
                idx = np.empty((nd, nc, nL), np.int16)
                for d in range(nd):
                    for k in range(nc):
                        idx[d, k] = RJ.cand_idx(donors, a.vtag, nL, d, k)
                pools[name] = RJ.masks_from(idx.reshape(-1, nL), Gall)
            for b, X in bal.items():
                t4, _ = RJ.pool_thresholds(pools["E4"], vid, X, (0.1, 0.01))
                t4b, _ = RJ.pool_thresholds(pools["E4b"], vid, X, (0.1, 0.01))
                for pa in (0.1, 0.01):
                    rows.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, n_L=nL, balance=b, p_a=pa,
                                     thr_E4_median=float(np.median(t4[pa])), thr_E4b_median=float(np.median(t4b[pa])),
                                     ratio_E4b_over_E4_median=float(np.median(t4b[pa] / t4[pa]))))
            print(est, nL, flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e4b_threshold__{a.vtag}__{a.arm}.csv"), index=False)


if __name__ == "__main__":
    raise SystemExit(main())
