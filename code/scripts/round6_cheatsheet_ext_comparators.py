"""Round 6 extension, cheatsheet track, C4.4: the round-1 anchor and the comparators.

Runs on Longleaf from a `git archive` copy (round6_cheatsheet_ext_comparators.sbatch).

The benchmark head is round 1's faithful pca_ridge head, as round 6 used it
(round6_cheatsheet_comparators.fit_head, imported unchanged): StandardScaler,
PCA to 256 components with random_state 1, then Ridge with alpha =
100 / (256 * 50), no intercept, solver lsqr, max_iter 1000. Its configuration
is read from results/faithful/pca_ridge/<encoder>/CCRCC/split0/config.json.

Anchor (instruction 6.7), from the project tree and not from the package. The
head is fitted on every patched spot of round 1's CCRCC split 0 training
slides and scored on every patched spot of its test slides, with round 1's
own metric, the mean over the 50 genes of the correlation pooled over the
test slides. It must reproduce results.json's pearson_mean within 0.01, for
both encoders.

Comparators, from the package, scored with the track's metric
(round6_cheatsheet_ext_score.score) on the 1,500 scored spots:
  head_sample    the head on the 3,500 writer spots, uni_v2 and virchow2
  head_all       the head on every patched spot of the 7 training slides
  codebook       uni_v2, k-means on the 3,500 writer spots with
                 k = min(floor(b/50), 3500), seed crc32("round6ext-codebook"),
                 cluster means quantised to one byte per gene over each gene's
                 range in the writer spots, nearest centroid for scored spots
  mean           each gene's mean over the writer spots, at every scored
                 spot. Its within-slide correlation is undefined, so only the
                 pooled value is meaningful, and it is 0 by the scorer's rule
                 for constant predictions.

    python round6_cheatsheet_ext_comparators.py --proj PROJECT_TREE --package DIR --out DIR
"""
import argparse
import json
import os
import sys

import h5py
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from round6_cheatsheet_comparators import codebook, fit_head  # noqa: E402
from round6_cheatsheet_ext_score import score  # noqa: E402
from round6_cheatsheet_score import score as pooled_score  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = "CCRCC"
ENCODERS = ("uni_v2", "virchow2")
SIZES = tuple(2 ** k for k in range(8, 17))


def head_config(encoder):
    d = os.path.join(REPO, "results/faithful/pca_ridge", encoder, TASK, "split0")
    return json.load(open(os.path.join(d, "config.json"))), json.load(open(os.path.join(d, "results.json")))


def decode(arr):
    return [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in np.asarray(arr).reshape(-1)]


def tree_slide(proj, sid, encoder, genes):
    """Embeddings and log1p target of every embedded spot of a slide, from the project tree."""
    import anndata as ad
    with h5py.File(os.path.join(proj, "embeddings", TASK, encoder, f"{sid}.h5"), "r") as f:
        bc = decode(f["barcodes" if "barcodes" in f else "barcode"][:])
        E = np.asarray(f["embeddings"][:], dtype=np.float32)
    A = ad.read_h5ad(os.path.join(proj, "bench_data", TASK, "adata", f"{sid}.h5ad"))
    sub = A[bc, genes]
    X = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
    return E, np.log1p(np.asarray(X, dtype=np.float64))


def anchor(proj, out):
    bd = os.path.join(proj, "bench_data", TASK)
    genes = json.load(open(os.path.join(bd, "var_50genes.json")))["genes"]
    tr = pd.read_csv(os.path.join(bd, "splits", "train_0.csv"))["sample_id"].tolist()
    te = pd.read_csv(os.path.join(bd, "splits", "test_0.csv"))["sample_id"].tolist()
    rows = []
    for e in ENCODERS:
        cfg, res = head_config(e)
        assert cfg["gene_list"] == "var_50genes.json" and cfg["normalize"] is True
        Xtr, Ytr = map(np.concatenate, zip(*[tree_slide(proj, s, e, genes) for s in tr]))
        Xte, Yte = map(np.concatenate, zip(*[tree_slide(proj, s, e, genes) for s in te]))
        pred = fit_head(Xtr, Ytr, Xte, cfg)
        idx = [str(i) for i in range(len(Yte))]
        rbar, pg = pooled_score(pd.DataFrame(pred, index=idx, columns=genes), pd.DataFrame(Yte, index=idx, columns=genes))
        ref = float(res["pearson_mean"])
        rows.append({"encoder": e, "split": "split0", "train_slides": " ".join(tr), "test_slides": " ".join(te),
                     "n_train": len(Ytr), "n_test": len(Yte), "pearson_mean": rbar, "round1_pearson_mean": ref,
                     "abs_diff": abs(rbar - ref), "passed": bool(abs(rbar - ref) <= 0.01),
                     "n_constant_pred": int(pg["constant_pred"].sum())})
        print(rows[-1], flush=True)
    a = pd.DataFrame(rows)
    a.to_csv(os.path.join(out, "anchor.csv"), index=False)
    return a


def load_package(pkg):
    genes = json.load(open(os.path.join(pkg, "genes.json")))["genes"]
    draws = json.load(open(os.path.join(pkg, "draws.json")))
    S = {}
    for sid in draws["slides"]:
        spots = pd.read_parquet(os.path.join(pkg, f"{sid}_spots.parquet"))
        t = pd.read_parquet(os.path.join(pkg, f"{sid}_target.parquet"))
        assert list(t["barcode"]) == list(spots["barcode"])
        S[sid] = {"bc": spots["barcode"].tolist(), "sampled": spots["sampled"].to_numpy(dtype=bool),
                  "Y": t[genes].to_numpy(dtype=np.float64),
                  "E": {e: np.load(os.path.join(pkg, f"{sid}_{e}.npy")) for e in ENCODERS}}
        assert S[sid]["sampled"].sum() == 500
    return genes, draws, S


def stack(S, sids, key, only_sampled, enc=None):
    parts = []
    for s in sids:
        M = S[s]["E"][enc] if key == "E" else S[s]["Y"]
        parts.append(M[S[s]["sampled"]] if only_sampled else M)
    return np.concatenate(parts)


def comparators(pkg, out):
    genes, draws, S = load_package(pkg)
    train, test = draws["train"], draws["test"]
    ids = [f"{s}:{b}" for s in test for b, m in zip(S[s]["bc"], S[s]["sampled"]) if m]
    slide = np.array([i.split(":")[0] for i in ids])
    truth = pd.DataFrame(stack(S, test, "Y", True), index=ids, columns=genes)
    Yw, Ya = stack(S, train, "Y", True), stack(S, train, "Y", False)
    assert Yw.shape == (3500, 50) and truth.shape == (1500, 50)
    rows, cells = [], []

    def add(name, enc, size, k, n_fit, pred):
        r = score(pd.DataFrame(pred, index=ids, columns=genes), truth, slide)
        row = {"comparator": name, "encoder": enc, "size": size, "k": k, "n_fit": n_fit, "n_scored": len(ids),
               "rbar": r["rbar"], "pooled": r["pooled"], "n_constant_pred_cells": r["n_constant_pred_cells"],
               "n_constant_truth_cells": r["n_constant_truth_cells"]}
        row.update({f"rbar_{s}": v for s, v in r["per_slide"].items()})
        rows.append(row)
        cells.append(r["cells"].assign(comparator=name, encoder=enc, size=str(size)))
        print({k_: (round(v, 4) if isinstance(v, float) else v) for k_, v in row.items()}, flush=True)

    for e in ENCODERS:
        cfg, _ = head_config(e)
        Xte = stack(S, test, "E", True, e)
        Xw, Xa = stack(S, train, "E", True, e), stack(S, train, "E", False, e)
        add("head_sample", e, "", "", len(Xw), fit_head(Xw, Yw, Xte, cfg))
        add("head_all", e, "", "", len(Xa), fit_head(Xa, Ya, Xte, cfg))
    Xw, Xte = stack(S, train, "E", True, "uni_v2"), stack(S, test, "E", True, "uni_v2")
    for b in SIZES:
        pred, k = codebook(Xw, Yw, Xte, b, seed_key="round6ext-codebook")
        add("codebook", "uni_v2", b, k, len(Xw), pred)
    add("mean", "", "", "", len(Yw), np.tile(Yw.mean(axis=0), (len(ids), 1)))
    pd.DataFrame(rows).to_csv(os.path.join(out, "comparators.csv"), index=False)
    pd.concat(cells).to_csv(os.path.join(out, "comparators_cells.csv"), index=False)
    const = truth.groupby(slide).agg(lambda c: np.ptp(c.to_numpy()) == 0)
    const.T.to_csv(os.path.join(out, "constant_truth_genes.csv"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj", required=True)
    ap.add_argument("--package", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    anc = anchor(a.proj, a.out)
    print(anc.to_string(index=False), flush=True)
    comparators(a.package, a.out)
    if not anc["passed"].all():
        sys.exit(3)


if __name__ == "__main__":
    main()
