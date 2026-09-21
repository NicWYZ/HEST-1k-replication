#!/usr/bin/env python
"""Round 2, stage R1: refit the benchmark head WITH an intercept.

Stage: R1, the three-head intercept refit (round2_execution_plan.md stage R1); superseded by round2_r1b_heads.py, which adds the exact and float64 solver families.

Why. The benchmark head is `Ridge(fit_intercept=False)` on PCA features that are centred
by construction, so its predictions have training mean zero for each gene while log1p(y)
has a positive mean. Pearson is invariant to that shift, so the benchmark never noticed;
R^2, absolute residuals, CRPS and interval width are not shift-invariant, so every Topic A
quantity is affected. Review section 5.6.

Three heads on IDENTICAL PCA-256 features from the identical round-1 pipeline
(StandardScaler -> PCA(256, random_state=1) fit on train only):

  nointercept  Ridge(alpha=100/(256*50), fit_intercept=False, solver='lsqr', max_iter=1000)
               -- the faithful head, as a control
  intercept    the same with fit_intercept=True
  ycentered    fit_intercept=False on y - ybar_train per gene, ybar_train added back to preds

Per fold and per gene this records: Pearson on the test fold computed the faithful way
(pooled over the fold, matching Table 1), R^2, MSE, mean of predictions, mean of targets,
and the same means on the TRAINING fold (which is what the mean-matching acceptance check
reads).

The full prediction arrays for the `intercept` head are written per (task, encoder) under
instrumentation/round2_intercept/<task>/preds__<encoder>.parquet, carrying the round-1 join
keys plus a `head` column, so the shards form one per-task dataset joinable to round 1 on
(task, encoder, fold, sample_id, barcode, gene). Sharding per encoder rather than appending
to one per-task file is what makes 12 concurrent encoder jobs safe.

Usage: round2_head_intercept.py <encoder>
"""
import glob
import json
import os
import sys
import time

import anndata as ad
import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scanpy as sc
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB = f"{ROOT}/bench_data", f"{ROOT}/embeddings"
OUT = f"{ROOT}/results/round2/R1_intercept"
PARQ = f"{ROOT}/instrumentation/round2_intercept"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"

SEED, LATENT = 1, 256
HEADS = ("nointercept", "intercept", "ycentered")

enc = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------------ data loading
def load_task(task):
    """Round-1 load_task, plus the barcodes and raw counts the parquet needs."""
    genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    Xs, Ys, Rs, samp, bcs = [], [], [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        with h5py.File(f"{EMB}/{task}/{enc}/{sid}.h5", "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
        A = ad.read_h5ad(p)
        raw = A[bc, genes]
        R = raw.X.toarray() if hasattr(raw.X, "toarray") else np.asarray(raw.X)
        Rs.append(np.asarray(R, dtype=np.float32))
        sc.pp.log1p(A)
        sub = A[bc, genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32))
        samp += [sid] * len(bc)
        bcs += bc
    return (np.vstack(Xs), np.vstack(Ys), np.vstack(Rs),
            np.array(samp), np.array(bcs, dtype=object), genes)


def features(Xtr, Xte):
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
    return pipe.fit_transform(Xtr), pipe.transform(Xte)


def fit_heads(A, B, Ytr):
    """Three heads x two solvers on the same features. Returns {head: (pred_test, pred_train)}.

    The `lsqr` family is the faithful head (round 1 used solver='lsqr', max_iter=1000 at
    sklearn's default tol). lsqr is ITERATIVE, so the three heads land at slightly
    different points even though they are algebraically identical:

      PCA centres the training features, so X'1 = 0. With fit_intercept=True the ridge
      coefficient solves the y-centred problem, w_int = w_noint - (X'X + aI)^-1 X' ybar 1,
      and X'1 = 0 kills the second term, so w_int == w_noint EXACTLY and b == ybar.
      Hence pred(intercept) == pred(nointercept) + ybar, a constant shift per gene, and
      ycentered is the same expression again.

    So the plan's acceptance thresholds (1e-6 on Pearson, 1e-4 on predictions, 1e-6 on the
    train-mean identity) are properties of the EXACT solve. The `cholesky` family is added
    to demonstrate that, and to separate solver tolerance from a pipeline difference.
    """
    alpha = 100 / (A.shape[1] * Ytr.shape[1])
    mu = Ytr.mean(axis=0, keepdims=True)
    out = {}
    for tag, kw in (("", dict(solver="lsqr", max_iter=1000)),
                    ("_exact", dict(solver="cholesky"))):
        r = Ridge(alpha=alpha, random_state=0, fit_intercept=False, **kw).fit(A, Ytr)
        out["nointercept" + tag] = (r.predict(B), r.predict(A))

        r = Ridge(alpha=alpha, random_state=0, fit_intercept=True, **kw).fit(A, Ytr)
        out["intercept" + tag] = (r.predict(B), r.predict(A))

        r = Ridge(alpha=alpha, random_state=0, fit_intercept=False, **kw).fit(A, Ytr - mu)
        out["ycentered" + tag] = (r.predict(B) + mu, r.predict(A) + mu)
    return out


def per_gene(P, Y, Ptr, Ytr, genes):
    """Faithful-way (pooled over the fold) per-gene metrics, plus training-fold means."""
    rows = []
    sst = ((Y - Y.mean(axis=0, keepdims=True)) ** 2).sum(axis=0)
    ssr = ((Y - P) ** 2).sum(axis=0)
    for j, g in enumerate(genes):
        if np.std(Y[:, j]) > 0 and np.std(P[:, j]) > 0:
            r = float(pearsonr(P[:, j], Y[:, j])[0])
        else:
            r = np.nan
        rows.append(dict(
            gene=g,
            pearson=r,
            r2=float(1.0 - ssr[j] / sst[j]) if sst[j] > 0 else np.nan,
            mse=float(ssr[j] / len(Y)),
            mean_pred=float(P[:, j].mean()),
            mean_target=float(Y[:, j].mean()),
            train_mean_pred=float(Ptr[:, j].mean()),
            train_mean_target=float(Ytr[:, j].mean())))
    return rows


# --------------------------------------------------------------------- main loop
sm = pd.read_csv(META)
pxmap = dict(zip(sm["sample_id"], sm.get("pixel_size_um", sm["pixel_size_um_estimated"])))
grpmap = dict(zip(sm["sample_id"], sm["resolution_group"])) if "resolution_group" in sm else {}

# Read round 1's preds.parquet schema. It is asserted against every shard before writing
# (see the write block below), which is what enforces the plan's "same schema as round 1
# plus a head column".
ref_cols = None
for t in sorted(os.listdir(f"{ROOT}/instrumentation")):
    rp = f"{ROOT}/instrumentation/{t}/preds.parquet"
    if os.path.exists(rp):
        ref_cols = pq.ParquetFile(rp).schema_arrow.names
        print(f"[schema] round-1 preds.parquet ({t}) columns: {ref_cols}", flush=True)
        break

rows = []
deltas = []
tasks = sorted(d for d in os.listdir(BD)
               if os.path.isdir(f"{BD}/{d}") and not d.startswith("."))
for task in tasks:
    if not glob.glob(f"{EMB}/{task}/{enc}/*.h5"):
        print(f"[skip] {task}: no embeddings for {enc}", flush=True)
        continue
    t0 = time.time()
    X, Y, R, samp, bc, genes = load_task(task)
    os.makedirs(f"{PARQ}/{task}", exist_ok=True)
    shards = []

    for sp in sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv")):
        k = int(os.path.basename(sp).split("_")[1].split(".")[0])
        test_ids = {os.path.basename(x).replace(".h5ad", "")
                    for x in pd.read_csv(sp)["expr_path"]}
        te = np.isin(samp, list(test_ids))
        tr = ~te
        assert te.sum() > 0 and tr.sum() > 0, f"{task} fold {k}: empty arm"

        A, B = features(X[tr], X[te])
        preds = fit_heads(A, B, Y[tr])

        for head, (P, Ptr) in preds.items():
            for row in per_gene(P, Y[te], Ptr, Y[tr], genes):
                rows.append(dict(encoder=enc, task=task, fold=k, head=head,
                                 n_train=int(tr.sum()), n_test=int(te.sum()),
                                 n_test_samples=len(test_ids), **row))

        # max |delta| between heads' predictions, per solver family, for the acceptance checks
        rec = dict(encoder=enc, task=task, fold=k)
        for tag in ("", "_exact"):
            ybar = Y[tr].mean(axis=0, keepdims=True)
            rec[f"max_abs_intercept_minus_ycentered{tag}"] = float(
                np.max(np.abs(preds["intercept" + tag][0] - preds["ycentered" + tag][0])))
            rec[f"max_abs_intercept_minus_nointercept{tag}"] = float(
                np.max(np.abs(preds["intercept" + tag][0] - preds["nointercept" + tag][0])))
            # the shift should equal ybar exactly (see fit_heads docstring)
            rec[f"max_abs_shift_minus_ybar{tag}"] = float(np.max(np.abs(
                (preds["intercept" + tag][0] - preds["nointercept" + tag][0]) - ybar)))
        deltas.append(rec)
        d_ni = rec["max_abs_intercept_minus_nointercept"]
        d_yc = rec["max_abs_intercept_minus_ycentered"]

        # prediction shards: the faithful-solver intercept head and the exact-solver one,
        # distinguished by the `head` column so downstream work can choose.
        for hname in ("intercept", "intercept_exact"):
            P = preds[hname][0]
            ns, ng = P.shape
            sh = pd.DataFrame({
                "task": task,
                "encoder": enc,
                "fold": k,
                "sample_id": np.repeat(samp[te], ng),
                "barcode": np.repeat(bc[te], ng),
                "gene": np.tile(np.asarray(genes, dtype=object), ns),
                "head": hname,
                # column names match round 1's instrumentation/<task>/preds.parquet
                # exactly (`pred`, `target`); y_raw_count is a declared addition.
                "pred": P.ravel().astype(np.float32),
                "target": Y[te].ravel().astype(np.float32),
                "y_raw_count": R[te].ravel().astype(np.float32),
            })
            sh["pixel_size_um"] = sh["sample_id"].map(pxmap).astype(np.float64)
            if grpmap:
                sh["resolution_group"] = sh["sample_id"].map(grpmap)
            shards.append(sh)
        print(f"  {task} fold{k}: n_train={tr.sum()} n_test={te.sum()} "
              f"max|int-noint|={d_ni:.3e} max|int-ycent|={d_yc:.3e}", flush=True)

    tab = pa.Table.from_pandas(pd.concat(shards, ignore_index=True), preserve_index=False)
    if ref_cols is not None:
        want = set(ref_cols) | {"head", "y_raw_count"}
        got = set(tab.column_names)
        assert got == want, (f"{task}: shard schema does not match round 1 plus "
                             f"{{head, y_raw_count}}; symmetric difference "
                             f"{sorted(got ^ want)}")
    pq.write_table(tab, f"{PARQ}/{task}/preds__{enc}.parquet", compression="snappy")
    print(f"[{task}] {tab.num_rows:,} rows written, {time.time()-t0:.0f}s", flush=True)
    del X, Y, R, shards

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/head_intercept__{enc}.csv", index=False)

# ------------------------------------------------------------------- acceptance
piv = d.pivot_table(index=["task", "fold", "gene"], columns="head",
                    values=["pearson", "r2", "mean_pred", "mean_target",
                            "train_mean_pred", "train_mean_target"])
dd = pd.DataFrame(deltas)
dd.to_csv(f"{OUT}/head_deltas__{enc}.csv", index=False)

print("\n=== R1 acceptance, by solver family ===")
print("(`lsqr` is the faithful head; `cholesky` is the exact solve. The three heads are "
      "algebraically identical up to a per-gene shift of ybar, so any deviation in the lsqr "
      "family is its iterative tolerance.)")
acc = []
for tag, fam in (("", "lsqr (faithful)"), ("_exact", "cholesky (exact)")):
    dp = (piv[("pearson", "intercept" + tag)] - piv[("pearson", "nointercept" + tag)]).abs()
    dtm = (piv[("train_mean_pred", "intercept" + tag)]
           - piv[("train_mean_target", "intercept" + tag)]).abs()
    a1, a2 = float(dp.max()), float(dd[f"max_abs_intercept_minus_ycentered{tag}"].max())
    a3 = float(dtm.max())
    a_shift = float(dd[f"max_abs_shift_minus_ybar{tag}"].max())
    for name, val, thr in (("A1 max|dPearson(int-noint)|", a1, 1e-6),
                           ("A2 max|pred(int)-pred(ycent)|", a2, 1e-4),
                           ("A3 max|train mean pred - target|", a3, 1e-6),
                           ("A2b max|(int-noint) - ybar|", a_shift, 1e-4)):
        acc.append(dict(encoder=enc, solver=fam, check=name, value=val,
                        threshold=thr, passed=bool(val < thr)))
        print(f"  {fam:<18} {name:<34} = {val:.3e}  [thr {thr:.0e}]  "
              f"{'PASS' if val < thr else 'FAIL'}")
pd.DataFrame(acc).to_csv(f"{OUT}/acceptance__{enc}.csv", index=False)

# A5: the `nointercept` control must reproduce round 1's faithful pca_ridge per-task Pearson.
# This is the check that actually establishes the pipeline is the faithful one.
rt_path = f"{ROOT}/results/summary/results_task.csv"
if os.path.exists(rt_path):
    rt = pd.read_csv(rt_path)
    rt = rt[(rt["head"] == "pca_ridge") & (rt["encoder"] == enc)][["task", "pearson_mean"]]
    ours = (d[d["head"] == "nointercept"].groupby(["task", "fold"])["pearson"].mean()
              .groupby("task").mean().rename("ours").reset_index())
    cmp = ours.merge(rt, on="task", how="outer")
    cmp["abs_diff"] = (cmp["ours"] - cmp["pearson_mean"]).abs()
    cmp.to_csv(f"{OUT}/faithful_check__{enc}.csv", index=False)
    print(f"A5 nointercept vs round-1 faithful pca_ridge, per task: "
          f"max |diff| = {cmp['abs_diff'].max():.3e}, mean {cmp['abs_diff'].mean():.3e} "
          f"over {cmp['abs_diff'].notna().sum()} tasks   [expect < 1e-3]  "
          f"{'PASS' if cmp['abs_diff'].max() < 1e-3 else 'FAIL'}")
    print(cmp.round(5).to_string(index=False))
else:
    print(f"A5 SKIPPED: {rt_path} absent")

fm = d.groupby(["task", "fold", "head"])["r2"].median().reset_index()
fp = fm.pivot_table(index=["task", "fold"], columns="head", values="r2")
print(f"A4 fold-median R^2 > 0: intercept {int((fp['intercept'] > 0).sum())}/{len(fp)} folds, "
      f"nointercept {int((fp['nointercept'] > 0).sum())}/{len(fp)} folds, "
      f"intercept_exact {int((fp['intercept_exact'] > 0).sum())}/{len(fp)} folds")
print("\nfold-median R^2 by task (mean over folds):")
print(fp.groupby(level=0).mean().round(4).to_string())
print("\nmean Pearson by task (intercept head, faithful pooled metric):")
print(d[d["head"] == "intercept"].groupby("task")["pearson"].mean().round(4).to_string())

with open(f"{OUT}/PROVENANCE__{enc}.txt", "w") as f:
    f.write(
        f"Round 2, stage R1 - intercept refit, encoder {enc}\n"
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
        f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
        f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
        f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
        f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
        f"script          : code/scripts/round2_head_intercept.py\n"
        f"command_line    : {' '.join(sys.argv)}\n"
        f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
        f"pipeline        : StandardScaler -> PCA({LATENT}, random_state={SEED}) on train only\n"
        f"alpha           : 100/(256*50)\n"
        f"heads           : {HEADS}\n"
        f"plan            : round2_execution_plan.md stage R1\n")
print(f"\nwrote {OUT}/head_intercept__{enc}.csv ({len(d)} rows)")
