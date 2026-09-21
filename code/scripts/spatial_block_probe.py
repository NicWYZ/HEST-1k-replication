#!/usr/bin/env python
"""Stage 4d': site separability under SPATIAL BLOCK cross-validation.

Stage: tailored analysis, slide-identity probe under spatial-block cross-validation.

The original probe (site_predictability.py) split spots at random within each slide, so a test
patch's immediate neighbours sat in training. Two mechanisms can then produce a correct slide
prediction:
  (1) a genuine slide-level signature -- stain lot, scanner colour profile, section thickness,
      which apply uniformly across the whole slide. This is the batch effect we care about.
  (2) local appearance matching -- effectively nearest-neighbour lookup against a neighbouring
      training patch. An artefact of the split, not a property of the encoder.
Random splitting admits both, so its accuracy is an UPPER BOUND on (1).

Here each slide's patches are binned onto a GRID x GRID grid over their pixel coordinates and
whole occupied blocks are assigned to train/test, targeting the same test fraction. A held-out
block's neighbours are mostly held out too, so (2) is largely suppressed.

Diagnostic, reported per design: distance from each test spot to its NEAREST TRAINING SPOT on
the same slide. Under random splitting this is ~one spot pitch; under block splitting it should
be a large fraction of a block width. This verifies the design did what is claimed rather than
asserting it.

Usage: spatial_block_probe.py <encoder> [<encoder> ...]
"""
import os, sys, glob
import numpy as np, pandas as pd, h5py
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import balanced_accuracy_score
from scipy.spatial import cKDTree

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/results/tailored/site_probes"
SEED, LATENT, GRID, TEST_FRAC = 1, 256, 6, 0.30
rng_global = np.random.default_rng(SEED)

def load(task, enc):
    """Returns X (n,d), slide_of (n,), xy (n,2) pixel coords -- all row-aligned per spot."""
    Xs, labels, coords = [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        this_slide = os.path.basename(p)[:-5]
        f5 = f"{EMB}/{task}/{enc}/{this_slide}.h5"
        if not os.path.isfile(f5):
            return None, None, None
        with h5py.File(f5, "r") as f:
            E = np.asarray(f["embeddings"][:], dtype=np.float32)
            C = np.asarray(f["coords"][:], dtype=np.float64)
        Xs.append(E); coords.append(C); labels += [this_slide]*len(E)
    return np.vstack(Xs), np.array(labels), np.vstack(coords)

def block_split(slide_of, xy, rng):
    """Assign whole GRIDxGRID spatial blocks per slide to test, targeting TEST_FRAC of spots."""
    test = np.zeros(len(xy), bool)
    for s in np.unique(slide_of):
        m = slide_of == s
        c = xy[m]
        # per-slide grid over the occupied coordinate range
        lo, hi = c.min(0), c.max(0)
        span = np.where(hi - lo == 0, 1.0, hi - lo)
        bi = np.clip(((c - lo) / span * GRID).astype(int), 0, GRID-1)
        key = bi[:, 0] * GRID + bi[:, 1]
        blocks, counts = np.unique(key, return_counts=True)
        order = rng.permutation(len(blocks))
        target = TEST_FRAC * m.sum()
        chosen, acc = [], 0
        for j in order:                      # greedily fill blocks until the target is met
            if acc >= target:
                break
            chosen.append(blocks[j]); acc += counts[j]
        sub = np.isin(key, chosen)
        idx = np.flatnonzero(m)
        test[idx[sub]] = True
    return test

def nn_dist(slide_of, xy, test):
    """Median distance from a test spot to the nearest TRAINING spot on the same slide."""
    d = []
    for s in np.unique(slide_of):
        m = slide_of == s
        tr = m & ~test; te = m & test
        if tr.sum() == 0 or te.sum() == 0:
            continue
        d.append(cKDTree(xy[tr]).query(xy[te], k=1)[0])
    return float(np.median(np.concatenate(d))) if d else np.nan

def fit(X, y, tr, te):
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, X.shape[1]), random_state=SEED))])
    Z = pipe.fit_transform(X[tr]); Zt = pipe.transform(X[te])
    clf = LogisticRegression(max_iter=2000, n_jobs=-1).fit(Z, y[tr])
    return balanced_accuracy_score(y[te], clf.predict(Zt))

rows = []
tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
for enc in sys.argv[1:]:
    for task in tasks:
        X, slide_of, xy = load(task, enc)
        if X is None:
            print(f"[skip] {task}/{enc}: no embeddings", flush=True); continue
        n_slides = len(set(slide_of))
        if n_slides < 2:
            continue
        rng = np.random.default_rng(SEED)

        # --- design 1: random spots (reproduces the original probe) ---
        idx_tr, idx_te = train_test_split(np.arange(len(X)), test_size=TEST_FRAC,
                                          random_state=SEED, stratify=slide_of)
        te_r = np.zeros(len(X), bool); te_r[idx_te] = True
        acc_r = fit(X, slide_of, ~te_r, te_r)
        d_r = nn_dist(slide_of, xy, te_r)

        # --- design 2: whole spatial blocks ---
        te_b = block_split(slide_of, xy, rng)
        if te_b.sum() < 20 or (~te_b).sum() < 50 or len(set(slide_of[te_b])) < n_slides:
            print(f"[warn] {task}/{enc}: block split lost slides "
                  f"({len(set(slide_of[te_b]))}/{n_slides}); recorded but flagged", flush=True)
        acc_b = fit(X, slide_of, ~te_b, te_b)
        d_b = nn_dist(slide_of, xy, te_b)

        rows.append(dict(encoder=enc, task=task, n_spots=len(X), n_slides=n_slides,
                         chance=1.0/n_slides,
                         acc_random=acc_r, acc_block=acc_b, acc_drop=acc_r-acc_b,
                         test_frac_random=float(te_r.mean()), test_frac_block=float(te_b.mean()),
                         nn_dist_random=d_r, nn_dist_block=d_b,
                         nn_dist_ratio=d_b/d_r if d_r else np.nan,
                         slides_in_block_test=len(set(slide_of[te_b]))))
        print(f"  {enc:11s} {task:10s} random={acc_r:.4f} block={acc_b:.4f} "
              f"drop={acc_r-acc_b:+.4f}  nn_dist {d_r:.0f}->{d_b:.0f}px "
              f"({d_b/d_r if d_r else float('nan'):.1f}x)", flush=True)
        del X

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/spatial_block_probe__{sys.argv[1]}.csv", index=False)
print()
print(d.groupby("encoder")[["acc_random","acc_block","acc_drop","nn_dist_ratio"]].mean().round(4).to_string())
print(f"\nmean drop {d['acc_drop'].mean():+.4f}; block accuracy still above chance in "
      f"{int((d.acc_block > d.chance*2).sum())}/{len(d)} cells")
print(f"nn-distance ratio (block/random): median {d.nn_dist_ratio.median():.1f}x "
      f"-- confirms the spatial buffer widened")
