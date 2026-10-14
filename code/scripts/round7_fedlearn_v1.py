#!/usr/bin/env python
"""Round 7 federated learning track, V1: the learning curve in donors (plan amendment A6).

One task per job, all three encoders. A fixed quarter of the donor units is the test set. From the
rest, the training pool, draws of 1, 2, 4, 8, 16 and all donor units are taken, 20 draws per size and
one at the full pool. Each draw's exact head is fitted from the sum of the chosen samples' sums; the
faithful head is fitted on the same draws at the two largest sizes.

Writes into its working directory (results/round7/fedlearn/V1/<task>/): v1_genes.json,
v1_summary.csv first, then v1_draws.csv, PROVENANCE.txt and _provenance.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round7_fedlearn_common as C  # noqa: E402
import round7_fedlearn_design as D  # noqa: E402
import round7_fedlearn_head as H  # noqa: E402

N_DRAWS = 20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--task", required=True, choices=["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"])
    ap.add_argument("--clone", default=C.CLONE)
    a = ap.parse_args()
    out = os.getcwd()
    C.stamp_dir(out, a.frame_id, note=f"round 7 fedlearn V1 {a.task}")
    t0 = time.time()
    td = H.load_td(a.clone, D.TASKS[a.task])
    td_cc = H.load_td(a.clone, D.TASKS["CCRCC"])
    sids = D.task_samples(td)
    units = D.units_of(td, sids)
    test_u, pool_u = D.v1_split(a.task, units)
    genes, gnote = D.gene_set(a.task, td, clone_td_ccrcc=td_cc)
    sizes = D.v1_sizes(len(pool_u))
    draws = {}
    for size in sizes:
        nd = 1 if size == len(pool_u) else N_DRAWS
        draws[size] = [sorted(H.rng_for("V1-draw", a.task, size, d).choice(pool_u, size=size, replace=False).tolist())
                       for d in range(nd)]
    json.dump(dict(task=a.task, genes=genes, gene_note=gnote, test_units=test_u, pool_units=pool_u,
                   sizes=sizes, draws={str(k): v for k, v in draws.items()}), open("v1_genes.json", "w"), indent=1)
    test_sids = [s for u in test_u for s in units[u]]
    rows = []
    for enc in D.ENCODERS:
        data = H.load_samples(td, sids, enc, genes)
        st = {s: H.Stats.of(data[s][0], data[s][1]) for s in sids}
        Xte = np.vstack([data[s][0] for s in test_sids])
        Yte = np.vstack([data[s][1] for s in test_sids])
        sl = np.concatenate([[s] * len(data[s][0]) for s in test_sids])
        for size in sizes:
            for d, chosen in enumerate(draws[size]):
                tr = [s for u in chosen for s in units[u]]
                heads = [("exact", H.fit_exact(H.total([st[s] for s in tr])))]
                if size in sizes[-2:]:
                    heads.append(("faithful", H.fit_faithful(np.vstack([data[s][0] for s in tr]),
                                                             np.vstack([data[s][1] for s in tr]))))
                for name, h in heads:
                    P = h.predict(Xte)
                    ws, nsl = H.within_slide(Yte, P, sl)
                    rows.append(dict(task=a.task, encoder=enc, size=size, draw=d, head=name,
                                     train_units=";".join(chosen), n_train_samples=len(tr),
                                     n_train_spots=int(sum(st[s].n for s in tr)), n_test_spots=len(Yte),
                                     within_slide=ws, n_test_slides_scored=nsl,
                                     pooled_pearson=H.pooled_pearson(Yte, P)))
        print(enc, "done", round(time.time() - t0), flush=True)
        del data, st
    R = pd.DataFrame(rows)
    S = (R.groupby(["task", "encoder", "head", "size"], sort=True)
         .agg(n_draws=("draw", "size"), within_slide_mean=("within_slide", "mean"),
              within_slide_sd=("within_slide", "std"), pooled_pearson_mean=("pooled_pearson", "mean"),
              pooled_pearson_sd=("pooled_pearson", "std"), n_train_spots_mean=("n_train_spots", "mean"))
         .reset_index())
    S.to_csv("v1_summary.csv", index=False)
    R.to_csv("v1_draws.csv", index=False)
    here = os.path.dirname(os.path.abspath(__file__))
    C.write_provenance(out, "V1", a.frame_id, " ".join([sys.executable] + sys.argv),
                       dict(task=a.task, n_draws=N_DRAWS, sizes=sizes, k=H.K_PC, lam_num=H.LAM_NUM,
                            min_slide_spots=H.MIN_SLIDE_SPOTS),
                       [os.path.abspath(__file__), C.__file__, H.__file__, D.__file__,
                        os.path.join(here, "round2_r2_gene_check.py")])
    print("wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
