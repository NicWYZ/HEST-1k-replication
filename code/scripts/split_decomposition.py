#!/usr/bin/env python
"""Stage 4b (v3): four split designs giving a THREE-TERM decomposition, metric held fixed.

Supersedes the two-gap version in the handoff and in split_comparison.py. Four defects in that
version, each of which inflates or confounds a reported gap:

1. THE METRIC MOVED WITH THE TEST SET. Pearson was computed on whatever spots the test set held.
   Under a random split the test set pools spots from every patient, so between-patient variance
   enters the denominator and the correlation is mechanically higher than within a homogeneous
   single-patient test set -- with an identical model. Part of (random - patient) was therefore
   aggregation, not leakage. FIX: compute Pearson WITHIN each patient and average, for EVERY
   design. Both versions are reported here so the size of the artefact is visible rather than
   assumed: pearson_pooled is the old metric, pearson_within is the fixed one.

2. LEAKAGE CONFLATED TWO MECHANISMS. A random spot split puts spatially adjacent near-duplicates
   of test spots into training (adjacent spots overlap in tissue and, on Visium, leak transcripts
   into each other). That is distinct from slide-level memorisation of stain and scanner
   signature. FIX: a fourth design, spatially blocked -- whole contiguous 6x6-grid blocks held
   out within each slide, so the same slides appear in train and test but adjacency is broken.

3. TRAINING SET SIZE MOVED TOO. Leave-source-out trains on a smaller, less diverse corpus, so
   part of any gap is "less data". FIX: the random and blocked designs take each shipped fold's
   test size, which makes their training size the complement and therefore identical to the
   patient design's. For the site-shift term, training size is matched by construction and
   asserted (see below).

4. SOURCE IS CONFOUNDED WITH PLATFORM AND ORGAN. Cohort source tracks technology (TENX is
   Xenium; ZEN, INT, MEND are Visium) and across tasks it tracks organ. The only clean
   within-task contrast is IDC, which has TENX and NCBI samples that are both Xenium on the same
   tissue. FIX: IDC is the headline site-shift result; cross-task transfer is a separate and more
   confounded analysis (across_task_shift.py).

The decomposition, all terms in within-patient Pearson:
    random  - blocked        spatial autocorrelation (adjacency leakage)
    blocked - patient        slide identity (stain/scanner memorisation)
    patient - source_unseen  site shift across institutions
Designs, and what each allows:
    random         same slides in train and test, adjacent spots too
    blocked        same slides, adjacency broken
    patient        slides disjoint (the shipped design)
    source_seen    slides disjoint, test slide's SOURCE present in training
    source_unseen  slides disjoint, test slide's source ABSENT from training
source_seen/source_unseen hold n_train and the test set identical and vary only source novelty.

Pipeline is the benchmark's, verbatim: StandardScaler -> PCA(256) fit on train only ->
Ridge(solver='lsqr', alpha=100/(d*n_genes), fit_intercept=False, max_iter=1000).
Usage: split_decomposition.py <encoder>
"""
import os, sys, json, glob
import numpy as np, pandas as pd, h5py, anndata as ad, scanpy as sc
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/results/tailored/splits"
SEED, LATENT, GRID, N_REPEATS, MIN_SPOTS = 1, 256, 6, 5, 50
enc = sys.argv[1]

def load_task(task):
    genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    Xs, Ys, samp, xy = [], [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        with h5py.File(f"{EMB}/{task}/{enc}/{sid}.h5", "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = [x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in b]
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
            xy.append(np.asarray(f["coords"][:], dtype=np.float64))
        A = ad.read_h5ad(p); sc.pp.log1p(A)
        sub = A[bc, genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32)); samp += [sid]*len(bc)
    return np.vstack(Xs), np.vstack(Ys), np.array(samp), np.vstack(xy), genes

def fit(Xtr, Xte, Ytr, Yte):
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
    A = pipe.fit_transform(Xtr); B = pipe.transform(Xte)
    reg = Ridge(solver="lsqr", alpha=100/(A.shape[1]*Ytr.shape[1]),
                random_state=0, fit_intercept=False, max_iter=1000).fit(A, Ytr)
    return reg.predict(B)

def score(P, Yte, samp_te):
    """pooled Pearson (the old, composition-dependent metric) and WITHIN-PATIENT Pearson."""
    pooled = [pearsonr(P[:, j], Yte[:, j])[0] for j in range(Yte.shape[1])
              if np.std(Yte[:, j]) > 0 and np.std(P[:, j]) > 0]
    pooled = float(np.mean(pooled)) if pooled else np.nan
    per_s = []
    for s in np.unique(samp_te):
        m = samp_te == s
        if m.sum() < MIN_SPOTS:
            continue
        rs = [pearsonr(P[m, j], Yte[m, j])[0] for j in range(Yte.shape[1])
              if np.std(Yte[m, j]) > 0 and np.std(P[m, j]) > 0]
        if rs:
            per_s.append(float(np.mean(rs)))
    return pooled, (float(np.mean(per_s)) if per_s else np.nan), len(per_s)

def block_test(samp, xy, target_frac, rng):
    """Hold out whole contiguous GRIDxGRID blocks per slide, ~target_frac of each slide's spots."""
    te = np.zeros(len(xy), bool)
    for s in np.unique(samp):
        m = samp == s; c = xy[m]
        lo, hi = c.min(0), c.max(0); span = np.where(hi-lo == 0, 1.0, hi-lo)
        key = (np.clip(((c-lo)/span*GRID).astype(int), 0, GRID-1) * [GRID, 1]).sum(1)
        blocks, counts = np.unique(key, return_counts=True)
        tgt, acc, chosen = target_frac*m.sum(), 0, []
        for j in rng.permutation(len(blocks)):
            if acc >= tgt: break
            chosen.append(blocks[j]); acc += counts[j]
        idx = np.flatnonzero(m); te[idx[np.isin(key, chosen)]] = True
    return te

rows = []
tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
for task in tasks:
    if not glob.glob(f"{EMB}/{task}/{enc}/*.h5"):
        print(f"[skip] {task}: no embeddings", flush=True); continue
    X, Y, samp, xy, genes = load_task(task)
    n = len(X)
    shipped = sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv"))

    # ---- patient (shipped), and random/blocked matched to each fold's test size ----
    for sp in shipped:
        k = int(os.path.basename(sp).split("_")[1].split(".")[0])
        test_ids = {os.path.basename(x).replace(".h5ad","") for x in pd.read_csv(sp)["expr_path"]}
        te = np.isin(samp, list(test_ids)); tr = ~te
        sz = int(te.sum())
        P = fit(X[tr], X[te], Y[tr], Y[te])
        po, wi, ns = score(P, Y[te], samp[te])
        rows.append(dict(encoder=enc, task=task, design="patient", fold=k, repeat=None,
                         n_train=int(tr.sum()), n_test=sz, n_eval_samples=ns,
                         pearson_pooled=po, pearson_within=wi))
        for rep in range(N_REPEATS):
            rng = np.random.default_rng(SEED + 977*rep + k)
            idx = rng.permutation(n); ter = np.zeros(n, bool); ter[idx[:sz]] = True
            P = fit(X[~ter], X[ter], Y[~ter], Y[ter])
            po, wi, ns = score(P, Y[ter], samp[ter])
            rows.append(dict(encoder=enc, task=task, design="random", fold=k, repeat=rep,
                             n_train=int((~ter).sum()), n_test=int(ter.sum()), n_eval_samples=ns,
                             pearson_pooled=po, pearson_within=wi))
            teb = block_test(samp, xy, sz/n, rng)
            P = fit(X[~teb], X[teb], Y[~teb], Y[teb])
            po, wi, ns = score(P, Y[teb], samp[teb])
            rows.append(dict(encoder=enc, task=task, design="blocked", fold=k, repeat=rep,
                             n_train=int((~teb).sum()), n_test=int(teb.sum()), n_eval_samples=ns,
                             pearson_pooled=po, pearson_within=wi))
        print(f"  {task} fold{k}: patient/random/blocked done (n_test={sz})", flush=True)

    # ---- site shift: identical test set and identical n_train, source novelty the only change ----
    src = np.array(["".join(ch for ch in s if ch.isalpha()) for s in samp])
    if len(set(src)) > 1:
        for t_samp in sorted(set(samp)):
            te = samp == t_samp
            s_t = src[te][0]
            same_other = (src == s_t) & ~te          # same source, different slide
            diff_src   = (src != s_t)                # the other source(s)
            if same_other.sum() == 0 or diff_src.sum() < MIN_SPOTS:
                continue
            n_train = int(diff_src.sum())            # the unseen arm has strictly less data
            pool_seen = np.flatnonzero(diff_src | same_other)
            for rep in range(N_REPEATS):
                rng = np.random.default_rng(SEED + 31*rep)
                tr_u = np.flatnonzero(diff_src)                       # source UNSEEN
                tr_s = rng.choice(pool_seen, size=n_train, replace=False)  # source SEEN
                assert len(tr_u) == len(tr_s) == n_train
                assert not set(tr_u) & set(np.flatnonzero(te))
                assert not set(tr_s) & set(np.flatnonzero(te))
                for nm, tri in (("source_unseen", tr_u), ("source_seen", tr_s)):
                    trm = np.zeros(n, bool); trm[tri] = True
                    P = fit(X[trm], X[te], Y[trm], Y[te])
                    po, wi, ns = score(P, Y[te], samp[te])
                    rows.append(dict(encoder=enc, task=task, design=nm, fold=t_samp, repeat=rep,
                                     n_train=n_train, n_test=int(te.sum()), n_eval_samples=ns,
                                     pearson_pooled=po, pearson_within=wi,
                                     test_slide=t_samp, test_source=s_t))
            print(f"  {task} site-shift hold={t_samp} ({s_t}) n_train={n_train} "
                  f"n_test={int(te.sum())}", flush=True)
    del X, Y

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/split_decomposition__{enc}.csv", index=False)

m = d.groupby("design")[["pearson_pooled","pearson_within"]].mean()
print("\n=== metric comparison (mean over all folds/repeats) ===")
print(m.round(4).to_string())
if {"random","patient"} <= set(m.index):
    print(f"\nleakage gap under the OLD pooled metric   : "
          f"{m.loc['random','pearson_pooled'] - m.loc['patient','pearson_pooled']:+.4f}")
    print(f"leakage gap under WITHIN-PATIENT Pearson  : "
          f"{m.loc['random','pearson_within'] - m.loc['patient','pearson_within']:+.4f}")
    print("  the difference is the aggregation artefact, not leakage")
if {"random","blocked","patient"} <= set(m.index):
    print(f"\n=== three-term decomposition (within-patient Pearson) ===")
    print(f"  spatial autocorrelation (random - blocked) : "
          f"{m.loc['random','pearson_within'] - m.loc['blocked','pearson_within']:+.4f}")
    print(f"  slide identity          (blocked - patient): "
          f"{m.loc['blocked','pearson_within'] - m.loc['patient','pearson_within']:+.4f}")
if {"source_seen","source_unseen"} <= set(m.index):
    print(f"  site shift (source_seen - source_unseen)   : "
          f"{m.loc['source_seen','pearson_within'] - m.loc['source_unseen','pearson_within']:+.4f}")
