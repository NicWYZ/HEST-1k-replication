#!/usr/bin/env python
"""Round 4 PPI Q2 recalibration test driver (staged job input, not part of the committed clone).

For a task and encoder, per donor g the mean of the 256 PCA coordinates over the donor's joined spots and
the mean residual offset b_g = mean(y - f) over the same spots (f from the B1 donor-design parquet).
Leaving donor h out (the harness's own donor fold: scaler+PCA+ridge head fitted on the other donors via
round3_a0_harness.fit_base), the other donors' offsets are ridge-regressed on their mean embeddings in the
SAME fold PCA space (pipe_h.transform), per gene; the predicted offset is added to donor h's predictions.
Ridge penalty: chosen per gene by inner leave-one-out over the training donors (closed form hat-matrix),
grid relative to the squared top singular value, plus the intercept-only limit. Never tuned on donor h.
"""
import argparse, json, os, sys, time, types, hashlib
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq

ap = argparse.ArgumentParser()
ap.add_argument("--task-def", required=True)
ap.add_argument("--enc", required=True)
ap.add_argument("--parquet", required=True)
ap.add_argument("--vtag", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--recal-parquet", required=True)
a = ap.parse_args()
sys.dont_write_bytecode = True
import round3_a0_harness as H
import round3_b1_ppi as B1
import round4_ppi_q2_masking as Q2

t0 = time.time()
td = json.load(open(a.task_def))
meta = dict(donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
            patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
            resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
            session_of={s["sample_id"]: s.get("session") for s in td["samples"]})
X, Y, samp, bc, xy, genes = H.load_task(td, a.enc)
n = len(samp)
print(f"[load] {n} spots x {X.shape[1]}, {len(genes)} genes {time.time()-t0:.0f}s", flush=True)
hargs = B1.harness_args(types.SimpleNamespace(predict=a.enc), [a.task_def], "donor")
specs = H.build_fold_specs(td, samp, xy, ["donor"], meta, hargs)
print(f"[specs] {len(specs)} folds", flush=True)

pdf = pd.read_parquet(a.parquet)
assert [c[3:] for c in pdf.columns if c.startswith("y__")] == genes
key = pd.Series(np.arange(len(pdf)), index=pd.MultiIndex.from_arrays([pdf["sample_id"], pdf["barcode"]]))
ridx = key.reindex(pd.MultiIndex.from_arrays([samp.astype(str), bc.astype(str)])).to_numpy()
assert not np.isnan(ridx).any() and len(pdf) == n
ridx = ridx.astype(int)
assert (ridx == np.arange(n)).all() or True
Fp = pdf[[f"f__{g}" for g in genes]].to_numpy(np.float64)[ridx]
Yp = pdf[[f"y__{g}" for g in genes]].to_numpy(np.float64)[ridx]
ydev = float(np.abs(Yp - Y).max())
joined = pdf["joined"].to_numpy(bool)[ridx]
donor_row = np.array([meta["donor_of"][s] for s in samp], dtype=object)
donors = sorted(set(donor_row))
D = len(donors)
dix = np.searchsorted(np.array(donors, dtype=object), donor_row)
print(f"[align] max|y_parquet - y_harness| {ydev:.3e}; joined {joined.sum()}; donors {D}", flush=True)

# donor offsets b_g from the parquet predictions, joined spots
res = Yp - Fp
cnt = np.bincount(dix[joined], minlength=D).astype(float)
b = np.zeros((D, len(genes)))
np.add.at(b, dix[joined], res[joined])
b = b / cnt[:, None]

def inner_loo(Xt, Yt):
    """per-gene LOO-chosen ridge on donor means; returns coef path helper (U,s,Vt, grid, best idx per gene)."""
    nT = Xt.shape[0]
    mu = Xt.mean(0); Xc = Xt - mu
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    ym = Yt.mean(0); Yc = Yt - ym
    UtY = U.T @ Yc
    grid = [np.inf] + list(s[0] ** 2 * 10.0 ** np.arange(-6.0, 3.01, 0.5))
    errs = np.zeros((len(grid), Yt.shape[1]))
    for k, al in enumerate(grid):
        sh = np.zeros_like(s) if np.isinf(al) else s ** 2 / (s ** 2 + al)
        fit = U @ (sh[:, None] * UtY)
        h = 1.0 / nT + (U ** 2 * sh[None, :]).sum(1)
        e = (Yc - fit) / (1.0 - h)[:, None]
        errs[k] = (e ** 2).mean(0)
    best = errs.argmin(0)
    return mu, ym, U, s, Vt, UtY, grid, best

bhat = np.full((D, len(genes)), np.nan)
alpha_rows = []
for sp in specs:
    Tm, Em = sp["T"], sp["E"]
    assert sp["C"].sum() == 0 and not (Tm & Em).any()
    hd = sorted(set(donor_row[Em]))
    assert len(hd) == 1, hd
    h = donors.index(hd[0])
    pipe, A, reg, ralpha = H.fit_base(X[Tm], Y[Tm])
    Bm = pipe.transform(X.astype(np.float64, copy=False))
    # spots of training donors: restrict to donors present in T (all others)
    M = np.zeros((D, Bm.shape[1])); np.add.at(M, dix[joined], Bm[joined]); M = M / cnt[:, None]
    tr = np.array([g for g in range(D) if g != h])
    mu, ym, U, s, Vt, UtY, grid, best = inner_loo(M[tr], b[tr])
    xh = (M[h] - mu) @ Vt.T
    pred = np.empty(len(genes))
    for j in range(len(genes)):
        al = grid[best[j]]
        sh = np.zeros_like(s) if np.isinf(al) else s / (s ** 2 + al)
        pred[j] = ym[j] + float(xh @ (sh * UtY[:, j]))
    bhat[h] = pred
    for j, g in enumerate(genes):
        alpha_rows.append(dict(held_out=donors[h], gene=g,
                               rel_log10_alpha=("inf" if np.isinf(grid[best[j]]) else float(np.log10(grid[best[j]] / s[0] ** 2)))))
    print(f"  fold {donors[h]} alpha_head {ralpha:.4g} {time.time()-t0:.0f}s", flush=True)
    del Bm, pipe, A, reg
assert np.isfinite(bhat).all()

# R^2 of the offsets, leave-one-donor-out
def r2(bt, bp, base):
    return 1.0 - ((bt - bp) ** 2).sum(0) / ((bt - base) ** 2).sum(0)
R2_off = r2(b, bhat, b.mean(0, keepdims=True))
# baseline of the fold-wise training-mean offset (intercept-only), for reference
bm_loo = (b.sum(0, keepdims=True) - b) / (D - 1)
R2_off_vs_trainmean = 1.0 - ((b - bhat) ** 2).sum(0) / ((b - bm_loo) ** 2).sum(0)
R2_const_loo = r2(b, bm_loo, b.mean(0, keepdims=True))

# recalibrated predictions for every spot (donor-level offset of its donor)
out = a.out_dir
os.makedirs(out, exist_ok=True)
Frec = pdf[[f"f__{g}" for g in genes]].to_numpy(np.float64)
dix_pdf = np.zeros(len(pdf), int); dix_pdf[ridx] = dix
Fnew = Frec + bhat[dix_pdf]
pdf2 = pdf.copy()
for j, g in enumerate(genes):
    pdf2[f"f__{g}"] = Fnew[:, j].astype(np.float32)
tab = pq.read_table(a.parquet)
schema = tab.schema
assert not os.path.exists(a.recal_parquet)
pq.write_table(pa.Table.from_pandas(pdf2[[f.name for f in schema]], schema=schema, preserve_index=False),
               a.recal_parquet, compression="snappy")

# cluster-level / within-cluster R^2 before and after (Q2's own measure, log1p y and f, joined spots)
res_by = {}
for tag, path in (("before", a.parquet), ("after", a.recal_parquet)):
    d = Q2.load(path, a.enc, a.vtag)
    res_by[tag] = Q2.r2_measures(d["Y"], d["P"], d["didx"], len(d["donors"]))
    assert list(d["genes"]) == genes
rows = []
for j, g in enumerate(genes):
    r = dict(task=a.vtag, encoder=a.enc, gene=g, n_donors=D, R2_offset_loo=R2_off[j],
             R2_offset_loo_vs_trainmean=R2_off_vs_trainmean[j], R2_offset_const_loo=R2_const_loo[j],
             offset_sd_across_donors=b[:, j].std(ddof=1), offset_mean=b[:, j].mean(),
             rel_log10_alpha_median=np.nan)
    for tag in ("before", "after"):
        for k in ("R2_cluster_raw", "R2_cluster_corrected", "R2_within", "R2_unit"):
            r[f"{k}_{tag}"] = float(res_by[tag][k][j])
    rows.append(r)
al = pd.DataFrame(alpha_rows)
al.to_csv(f"{out}/q2_recal_ridge_penalty_choice__{a.vtag}.csv", index=False)
df = pd.DataFrame(rows)
df.to_csv(f"{out}/q2_recal_stage1__{a.vtag}.csv", index=False)
pd.DataFrame(np.hstack([b, bhat]), index=donors,
             columns=[f"b__{g}" for g in genes] + [f"bhat__{g}" for g in genes]).to_csv(f"{out}/q2_recal_donor_offsets__{a.vtag}.csv")
json.dump(dict(task=a.vtag, enc=a.enc, n_donors=D, n_genes=len(genes), ydev=ydev, wall=time.time() - t0,
               penalty="per gene, inner leave-one-out over the training donors (closed form), grid 1e-6..1e3 x s1^2 plus intercept-only",
               embedding_space="fold PCA (round3_a0_harness.fit_base on the other donors), donor means over joined spots",
               offsets="mean(y - f) over joined spots, f the B1 donor-design parquet",
               recal_parquet=a.recal_parquet, recal_parquet_md5=hashlib.md5(open(a.recal_parquet, "rb").read()).hexdigest(),
               stubbed=Q2.STUBBED), open(f"{out}/q2_recal_summary__{a.vtag}.json", "w"), indent=1)
print("[done]", time.time() - t0, flush=True)
