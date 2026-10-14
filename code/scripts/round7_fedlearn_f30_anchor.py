#!/usr/bin/env python
"""Round 7 federated learning track, F3.0: the two anchors (plan amendment A5).

(1) The faithful pca_ridge head for uni_v2 on CCRCC on round 1's six splits, through HEST-bench's
own functions (load_adata, read_assets_from_h5, the scaler and PCA pipeline, train_test_reg), against
round 1's stored pearson_mean, within 0.001. The session's scikit-learn copy of the faithful head
(round7_fedlearn_head.fit_faithful) is run on the same splits and must agree.
(2) The exact head fitted from per-center sums and from pooled spot arrays, on every center split
of V2 with uni_v2, compared on predictions for every spot: max |difference| / max |pooled|, below 1e-8.

Writes into its working directory (results/round7/fedlearn/F3_anchor/): f30_summary.json first,
then f30_faithful.csv and f30_exact.csv, PROVENANCE.txt and _provenance.json.
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

TOL_FAITHFUL = 1e-3
TOL_EXACT = 1e-8


def faithful_anchor(clone):
    import torch
    from sklearn.decomposition import PCA
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from hest.bench.st_dataset import load_adata
    from hest.bench.trainer import train_test_reg
    from hest.bench.utils.file_utils import read_assets_from_h5
    bd = f"{H.ROOT}/bench_data/CCRCC"
    emb = f"{H.ROOT}/embeddings/CCRCC/uni_v2"
    genes = json.load(open(f"{bd}/var_50genes.json"))["genes"]
    r1 = json.load(open(os.path.join(clone, "results/faithful/pca_ridge/uni_v2/CCRCC/results_kfold.json")))
    rows = []
    for i in range(6):
        assets_split = {}
        for key in ("train", "test"):
            df = pd.read_csv(f"{bd}/splits/{key}_{i}.csv")
            Xs, Ys, sl = [], [], []
            for r in df.itertuples():
                a, _ = read_assets_from_h5(f"{emb}/{r.sample_id}.h5")
                bc = a["barcodes"].flatten().astype(str).tolist()
                ad_ = load_adata(f"{bd}/{r.expr_path}", genes=genes, barcodes=bc, normalize=True)
                Xs.append(a["embeddings"])
                Ys.append(ad_.values)
                sl += [r.sample_id] * len(bc)
            assets_split[key] = (np.concatenate(Xs), np.concatenate(Ys), np.array(sl))
        Xtr, ytr, _ = assets_split["train"]
        Xte, yte, sl_te = assets_split["test"]
        pipe = Pipeline([("scaler", StandardScaler()), ("PCA", PCA(n_components=256, random_state=1))])
        Ztr, Zte = torch.Tensor(pipe.fit_transform(Xtr)), torch.Tensor(pipe.transform(Xte))
        res, _ = train_test_reg(Ztr, Zte, ytr, yte, random_state=1, genes=genes, method="ridge")
        rep = H.fit_faithful(Xtr, ytr)
        P = rep.predict(Xte)
        rep_pm = H.pooled_pearson(yte, P)
        ws, nsl = H.within_slide(yte, P, sl_te)
        rows.append(dict(split=i, n_train=len(ytr), n_test=len(yte), hest_pearson_mean=res["pearson_mean"],
                         replica_pearson_mean=rep_pm, replica_minus_hest=rep_pm - res["pearson_mean"],
                         round1_mean_per_split=r1["mean_per_split"][i], replica_within_slide=ws,
                         n_test_slides_scored=nsl))
    F = pd.DataFrame(rows)
    return F, float(r1["pearson_mean"]) if "pearson_mean" in r1 else float(np.mean(r1["mean_per_split"]))


def exact_anchor(clone):
    td_cc = H.load_td(clone, D.TASKS["CCRCC"])
    specs = []
    for task in ("KIDNEY_POP54", "BREAST_XENIUM"):
        td = H.load_td(clone, D.TASKS[task])
        sids = D.task_samples(td)
        specs.append((task, "V2a_sources", td, D.sources(task, td, sids)))
    for task in ("CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"):
        td = H.load_td(clone, D.TASKS[task])
        sids = D.task_samples(td)
        units = D.units_of(td, sids)
        part = D.partitions(task, units)[0]
        specs.append((task, "V2b_partition0", td, {c: [s for u in us for s in units[u]] for c, us in part.items()}))
    rows, genes_used = [], {}
    for task, design, td, centers in specs:
        if task == "BREAST_XENIUM":
            genes, _ = H.select_genes(td, sorted(s for v in centers.values() for s in v), "uni_v2")
        else:
            genes, _ = D.gene_set(task, td, clone_td_ccrcc=td_cc)
        genes_used[task] = genes
        sids = sorted(s for v in centers.values() for s in v)
        data = H.load_samples(td, sids, "uni_v2", genes)
        st = {c: H.total([H.Stats.of(data[s][0], data[s][1]) for s in v]) for c, v in centers.items()}
        h_sum = H.fit_exact(H.total(list(st.values())))
        X = np.vstack([data[s][0] for s in sids])
        Y = np.vstack([data[s][1] for s in sids])
        h_pool = H.fit_exact_pooled_arrays(X, Y)
        P_sum, P_pool = h_sum.predict(X), h_pool.predict(X)
        rd = H.rel_diff(P_sum, P_pool)
        rows.append(dict(task=task, design=design, n_centers=len(centers), n_samples=len(sids), n_spots=len(X),
                         n_genes=len(genes), rel_diff=rd, passes=rd < TOL_EXACT,
                         pooled_pearson_in_sample=H.pooled_pearson(Y, P_pool)))
        del data, X, Y
    return pd.DataFrame(rows), genes_used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--clone", default=C.CLONE)
    a = ap.parse_args()
    out = os.getcwd()
    C.stamp_dir(out, a.frame_id, note="round 7 fedlearn F3.0 anchors")
    t0 = time.time()
    F, r1_mean = faithful_anchor(a.clone)
    E, genes_used = exact_anchor(a.clone)
    hest_mean = float(F.hest_pearson_mean.mean())
    summary = dict(
        faithful=dict(hest_mean_over_splits=hest_mean, round1_pearson_mean=r1_mean,
                      abs_diff=abs(hest_mean - r1_mean), tol=TOL_FAITHFUL, passes=abs(hest_mean - r1_mean) < TOL_FAITHFUL,
                      replica_max_abs_diff_vs_hest=float(F.replica_minus_hest.abs().max())),
        exact=dict(max_rel_diff=float(E.rel_diff.max()), tol=TOL_EXACT, passes=bool(E.passes.all()), n_designs=len(E)),
        genes_used=genes_used, wall_seconds=round(time.time() - t0, 1))
    json.dump(summary, open("f30_summary.json", "w"), indent=2)
    F.to_csv("f30_faithful.csv", index=False)
    E.to_csv("f30_exact.csv", index=False)
    here = os.path.dirname(os.path.abspath(__file__))
    C.write_provenance(out, "F3.0", a.frame_id, " ".join([sys.executable] + sys.argv),
                       dict(tol_faithful=TOL_FAITHFUL, tol_exact=TOL_EXACT, k=H.K_PC, lam_num=H.LAM_NUM),
                       [os.path.abspath(__file__), C.__file__, H.__file__, D.__file__,
                        os.path.join(here, "round2_r2_gene_check.py")])
    print(json.dumps({k: v for k, v in summary.items() if k != "genes_used"}, indent=1))


if __name__ == "__main__":
    main()
