#!/usr/bin/env python
"""Round 7 federated learning track, V4: partial gene overlap (plan amendment A9), on V2(b).

Each center measures a random half (25) of the 50 target genes, drawn independently per center,
10 masks per partition. The basis comes from all training centers' embedding sums. Each gene's ridge
is fitted from the training centers that measure it, with that subset's own centring and intercept
and the full-panel penalty lambda = 100 / (256 * 50). A gene no training center measures is counted
and left out of both arms' metrics. The comparator is the full-overlap federated head on the same
partition. Masks apply to training labels only; scoring uses the full measured expression.
Schemes as V2: within (held-out donors of each center) and loco (leave one center out).

One job per task, all three encoders. Writes into its working directory
(results/round7/fedlearn/V4/<task>/): v4_genes.json, v4_summary.csv and v4_paired.csv first, then
v4_rows.csv, PROVENANCE.txt and _provenance.json.
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
import round7_fedlearn_v2 as V2  # noqa: E402

N_MASKS = 10
N_MEASURED = 25


def masked_predict(st_by_center, mask, X, q, basis):
    """Predictions for every gene (NaN where no training center measures it). mask: center -> set of
    gene indices that center measures. basis: from all training centers' embedding sums."""
    lam = H._lam(q)
    P = np.full((len(X), q), np.nan)
    groups = {}
    for g in range(q):
        who = tuple(sorted(c for c in st_by_center if g in mask[c]))
        if who:
            groups.setdefault(who, []).append(g)
    for who, gs in groups.items():
        st = V2.sub(H.total([st_by_center[c] for c in who]), gs)
        h = H.fit_exact(st, lam=lam, basis=basis)
        P[:, gs] = h.predict(X)
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--task", required=True, choices=["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"])
    ap.add_argument("--clone", default=C.CLONE)
    a = ap.parse_args()
    out = os.getcwd()
    C.stamp_dir(out, a.frame_id, note=f"round 7 fedlearn V4 {a.task}")
    t0 = time.time()
    td = H.load_td(a.clone, D.TASKS[a.task])
    td_cc = H.load_td(a.clone, D.TASKS["CCRCC"])
    sids = D.task_samples(td)
    des = V2.designs(a.task, td, sids)
    genes, gnote = D.gene_set(a.task, td, clone_td_ccrcc=td_cc)
    q = len(genes)
    masks = {(d["draw"], m): {c: set(H.rng_for("V4-mask", a.task, d["draw"], m, c)
                                     .choice(q, size=N_MEASURED, replace=False).tolist()) for c in d["allc"]}
             for d in des for m in range(N_MASKS)}
    json.dump(dict(task=a.task, genes=genes, gene_note=gnote,
                   masks={f"{p}|{m}": {c: sorted(v) for c, v in mk.items()} for (p, m), mk in masks.items()}),
              open("v4_genes.json", "w"), indent=1)
    allg = list(range(q))
    rows = []
    for enc in D.ENCODERS:
        T = V2.Task(td, sids, enc, genes)
        for d in des:
            st_tr = {c: T.stats(v, allg) for c, v in d["train"].items()}
            st_all = {c: T.stats(v, allg) for c, v in d["allc"].items()}
            evals = [("within", c, {k: st_tr[k] for k in st_tr}, d["held"][c]) for c in d["train"]]
            evals += [("loco", c, {k: st_all[k] for k in st_all if k != c}, d["allc"][c]) for c in d["allc"]]
            for scheme, c, st, test_sids in evals:
                X, Y, sl = T.test(test_sids, allg)
                tot = H.total(list(st.values()))
                basis = H.basis_from(tot)
                P_full = H.fit_exact(tot).predict(X)
                for m in range(N_MASKS):
                    mk = masks[(d["draw"], m)]
                    P_m = masked_predict(st, mk, X, q, basis)
                    keep = np.where(~np.isnan(P_m[0]))[0]
                    base = dict(task=a.task, encoder=enc, partition=d["draw"], mask=m, scheme=scheme, center=c,
                                n_genes_fitted=len(keep), n_genes_excluded=q - len(keep), n_test_spots=len(Y))
                    for arm, P in (("masked", P_m), ("full_overlap", P_full)):
                        rows.append({**base, "arm": arm, **V2.score(Y[:, keep], P[:, keep], sl)})
        print(enc, "done", round(time.time() - t0), flush=True)
        del T
    R = pd.DataFrame(rows)
    keys = ["task", "encoder", "scheme"]
    per = R.groupby(keys + ["partition", "mask", "arm"])[["within_slide", "pooled_pearson", "n_genes_excluded"]].mean().reset_index()
    S = (per.groupby(keys + ["arm"]).agg(n=("mask", "size"), within_slide_mean=("within_slide", "mean"),
                                         within_slide_sd=("within_slide", "std"),
                                         pooled_pearson_mean=("pooled_pearson", "mean"),
                                         pooled_pearson_sd=("pooled_pearson", "std"),
                                         n_genes_excluded_mean=("n_genes_excluded", "mean")).reset_index())
    pv = per.pivot_table(index=keys + ["partition", "mask"], columns="arm", values=["within_slide", "pooled_pearson"])
    prs = []
    for mtr in ("within_slide", "pooled_pearson"):
        dlt = (pv[(mtr, "masked")] - pv[(mtr, "full_overlap")]).rename("diff").reset_index()
        for g, h in dlt.groupby(keys):
            prs.append(dict(zip(keys, g), metric=mtr, n=len(h), mean_diff=h["diff"].mean(), sd_diff=h["diff"].std(),
                            min_diff=h["diff"].min(), n_below=int((h["diff"] < 0).sum())))
    S.to_csv("v4_summary.csv", index=False)
    pd.DataFrame(prs).to_csv("v4_paired.csv", index=False)
    R.to_csv("v4_rows.csv", index=False)
    here = os.path.dirname(os.path.abspath(__file__))
    C.write_provenance(out, "V4", a.frame_id, " ".join([sys.executable] + sys.argv),
                       dict(task=a.task, n_masks=N_MASKS, n_measured=N_MEASURED, k=H.K_PC, lam_num=H.LAM_NUM),
                       [os.path.abspath(__file__), C.__file__, H.__file__, D.__file__, V2.__file__,
                        os.path.join(here, "round2_r2_gene_check.py")])
    print("wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
