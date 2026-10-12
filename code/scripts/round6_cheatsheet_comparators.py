"""Round 6 cheatsheet track, C0.4: the comparators and the round-1 anchor.

The benchmark head is round 1's faithful pca_ridge head (HEST benchmark.py,
as re-implemented and checked in code/scripts/round2_r1b_heads.py):
StandardScaler, PCA to 256 components with random_state 1, then Ridge with
alpha = 100 / (256 * 50), no intercept, solver lsqr, max_iter 1000, on the
float32 embeddings. Its configuration is read from
results/faithful/pca_ridge/<encoder>/SKCM/split<k>/config.json.

Anchor: fitted on every spot of one slide and scored on every spot of the
other, it must reproduce round 1's per-direction mean Pearson within 0.01.

Comparators on S1* and S2*, fitted on the spots each arm's writer sees:
  arm A  all S1 spots, scored on S1* (in-sample)
  arm B  S1 training-block spots, scored on S1*
  arm C  all S1 spots, scored on S2*
  head      uni_v2 and hoptimus1
  codebook  uni_v2, k-means with k = min(floor(b/50), n) on the writer's spots,
            seed crc32("round6-codebook"), cluster means quantised to one byte
            per gene over each gene's range in the writer's spots, nearest
            centroid for the scored spots. For k = n every spot is its own
            centroid (nearest-neighbour lookup).

    python round6_cheatsheet_comparators.py --private /srv/r6_private --out DIR
"""
import argparse
import json
import os
import sys
import zlib

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from round6_cheatsheet_score import score  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENCODERS = ("uni_v2", "hoptimus1")
SIZES = (4096, 32768, 262144)


def head_config(encoder, split):
    d = os.path.join(REPO, "results/faithful/pca_ridge", encoder, "SKCM", split)
    cfg = json.load(open(os.path.join(d, "config.json")))
    res = json.load(open(os.path.join(d, "results.json")))
    return cfg, res


def fit_head(Xtr, Ytr, Xte, cfg):
    latent = int(cfg["latent_dim"])
    assert cfg["method"] == "ridge" and cfg["dimreduce"] == "PCA" and cfg["alpha"] is None
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(latent, Xtr.shape[1]), random_state=int(cfg["seed"])))])
    A = pipe.fit_transform(Xtr)
    B = pipe.transform(Xte)
    alpha = 100 / (A.shape[1] * Ytr.shape[1])
    reg = Ridge(alpha=alpha, random_state=0, fit_intercept=False, solver="lsqr", max_iter=1000)
    reg.fit(A, Ytr)
    return reg.predict(B)


def codebook(Xtr, Ytr, Xte, b, seed_key="round6-codebook"):
    n = Xtr.shape[0]
    k = min(b // 50, n)
    lo, hi = Ytr.min(axis=0), Ytr.max(axis=0)
    span = np.where(hi > lo, hi - lo, 1.0)
    if k >= n:
        centroids, means = Xtr, Ytr
    else:
        km = KMeans(n_clusters=k, random_state=zlib.crc32(seed_key.encode()), n_init=1).fit(Xtr)
        centroids = km.cluster_centers_
        means = np.vstack([Ytr[km.labels_ == c].mean(axis=0) for c in range(k)])
    q = np.round((means - lo) / span * 255).clip(0, 255)
    deq = lo + q / 255 * span
    # nearest centroid by squared Euclidean distance, in blocks to bound memory
    out = np.empty((Xte.shape[0], Ytr.shape[1]))
    c2 = (centroids.astype(np.float64) ** 2).sum(1)
    for s in range(0, Xte.shape[0], 256):
        x = Xte[s:s + 256].astype(np.float64)
        d = c2[None, :] - 2 * x @ centroids.astype(np.float64).T
        out[s:s + 256] = deq[np.argmin(d, axis=1)]
    return out, k


def load(private):
    pkg = os.path.join(private, "package")
    genes = json.load(open(os.path.join(pkg, "genes.json")))["genes"]
    S = {}
    for tag in ("S1", "S2"):
        spots = pd.read_parquet(os.path.join(pkg, f"{tag}_spots.parquet"))
        t = pd.read_parquet(os.path.join(pkg, f"{tag}_target.parquet"))
        assert list(t["barcode"]) == list(spots["barcode"])
        S[tag] = {"spots": spots, "Y": t[genes].to_numpy(dtype=np.float64),
                  "E": {e: np.load(os.path.join(pkg, f"{tag}_{e}.npy")) for e in ENCODERS}}
        for e in ENCODERS:
            assert S[tag]["E"][e].shape[0] == len(spots)
    splits = json.load(open(os.path.join(pkg, "splits.json")))
    return genes, S, splits


def frame(Y, idx, genes):
    """Rows idx of a full-slide matrix Y."""
    return pd.DataFrame(Y[idx], index=[str(i) for i in idx], columns=genes)


def pred_frame(P, idx, genes):
    """Predictions already computed for the rows idx, in that order."""
    assert P.shape[0] == len(idx)
    return pd.DataFrame(P, index=[str(i) for i in idx], columns=genes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--private", default="/srv/r6_private")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    genes, S, splits = load(a.private)
    slide_of = {"TENX115": "S1", "TENX117": "S2"}

    # anchor
    rows, per_gene = [], []
    for e in ENCODERS:
        for split in ("split0", "split1"):
            cfg, res = head_config(e, split)
            tr = slide_of[splits[split]["train"][0]]
            te = slide_of[splits[split]["test"][0]]
            pred = fit_head(S[tr]["E"][e], S[tr]["Y"], S[te]["E"][e], cfg)
            idx = np.arange(len(S[te]["Y"]))
            rbar, pg = score(pred_frame(pred, idx, genes), frame(S[te]["Y"], idx, genes))
            ref = float(res["pearson_mean"])
            rows.append({"encoder": e, "split": split, "train": tr, "test": te, "n_train": len(S[tr]["Y"]),
                         "n_test": len(idx), "rbar": rbar, "round1_pearson_mean": ref,
                         "abs_diff": abs(rbar - ref), "passed": abs(rbar - ref) <= 0.01,
                         "n_constant_pred": int(pg["constant_pred"].sum())})
    anchor = pd.DataFrame(rows)
    anchor.to_csv(os.path.join(a.out, "anchor.csv"), index=False)
    print(anchor.to_string(index=False))

    # comparators
    s1, s2 = S["S1"], S["S2"]
    star1 = np.flatnonzero(s1["spots"]["in_S1star"].to_numpy())
    star2 = np.flatnonzero(s2["spots"]["in_S2star"].to_numpy())
    fit_sets = {"A": np.arange(len(s1["Y"])), "B": np.flatnonzero(~s1["spots"]["heldout"].to_numpy()),
                "C": np.arange(len(s1["Y"]))}
    scored = {"A": ("S1star", s1, star1), "B": ("S1star", s1, star1), "C": ("S2star", s2, star2)}
    rows = []
    for arm in ("A", "B", "C"):
        fit = fit_sets[arm]
        name, sc, idx = scored[arm]
        truth = frame(sc["Y"], idx, genes)
        for e in ENCODERS:
            cfg, _ = head_config(e, "split0")
            pred = fit_head(s1["E"][e][fit], s1["Y"][fit], sc["E"][e][idx], cfg)
            rbar, pg = score(pred_frame(pred, idx, genes), truth)
            rows.append({"comparator": "benchmark_head", "encoder": e, "arm": arm, "size": "", "k": "",
                         "scored_set": name, "n_fit": len(fit), "n_scored": len(idx), "rbar": rbar,
                         "n_constant_pred": int(pg["constant_pred"].sum())})
            per_gene.append(pg.assign(comparator="benchmark_head", encoder=e, arm=arm, size=""))
        for b in SIZES:
            pred, k = codebook(s1["E"]["uni_v2"][fit], s1["Y"][fit], sc["E"]["uni_v2"][idx], b)
            rbar, pg = score(pred_frame(pred, idx, genes), truth)
            rows.append({"comparator": "codebook", "encoder": "uni_v2", "arm": arm, "size": b, "k": k,
                         "scored_set": name, "n_fit": len(fit), "n_scored": len(idx), "rbar": rbar,
                         "n_constant_pred": int(pg["constant_pred"].sum())})
            per_gene.append(pg.assign(comparator="codebook", encoder="uni_v2", arm=arm, size=b))
    comp = pd.DataFrame(rows)
    comp.to_csv(os.path.join(a.out, "comparators.csv"), index=False)
    pg = pd.concat(per_gene)
    pg["size"] = pg["size"].astype(str)
    pg.to_csv(os.path.join(a.out, "comparators_per_gene.csv"), index=False)
    print(comp.to_string(index=False))
    if not anchor["passed"].all():
        sys.exit(3)


if __name__ == "__main__":
    main()
