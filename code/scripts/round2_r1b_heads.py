#!/usr/bin/env python
"""Round 2, stage R1: refit the benchmark head WITH an intercept.

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
# R1b writes to its own directory. results/round2/R1_intercept stays as the 11-encoder
# float32 record reported at the R1 gate; R1b supersedes it with 12 encoders and three
# solver families, which also closes the conch_v15 gap (oversight directive D1) without a
# lone resubmission.
OUT = f"{ROOT}/results/round2/R1b_heads"
PARQ = f"{ROOT}/instrumentation/round2_intercept_f64"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"

SEED, LATENT = 1, 256
HEADS = ("nointercept", "intercept", "ycentered")

enc = sys.argv[1]
# FAMILY: 'all' (default), 'f32' (the two float32 families), or 'f64' (the float64 family
# only). The f64-only mode exists because the first R1b run built the float64 arm on
# float32-derived features, which is a bug in the arm and not in the float32 results; the
# corrected pass redoes only what was wrong. Outputs are suffixed so a partial pass cannot
# overwrite the arms it did not recompute.
FAMILY = sys.argv[2] if len(sys.argv) > 2 else "all"
assert FAMILY in ("all", "f32", "f64"), FAMILY
SUF = "" if FAMILY == "all" else f"__{FAMILY}"
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


def features(Xtr, Xte, dtype=np.float32):
    """Round 1's feature pipeline, with the working dtype exposed.

    The dtype is load-bearing and getting it wrong was a real bug in the first R1b run.
    The three-head identity rests on PCA centring the training features exactly, so that
    A'1 = 0 and the intercept fit has the same coefficients as the no-intercept fit. Running
    the scaler and PCA in float32 and casting the RESULT to float64 does not buy that: the
    column means of A land at ~5e-08 rather than ~1e-16, w_int and w_noint then differ at
    ~3e-08, and the identity holds only to ~7e-07 no matter how exact the ridge solve is.
    Casting X BEFORE the scaler drops the column means to ~1e-16 and the identity to
    ~2e-15. Measured both ways; see the R3 report.
    """
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
    return (pipe.fit_transform(Xtr.astype(dtype, copy=False)),
            pipe.transform(Xte.astype(dtype, copy=False)))


def fit_heads(A, B, Ytr, A64=None, B64=None):
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

    Round 2 R1b, oversight Decision 1: a THIRD family is added in float64 with the exact
    solver. Under exact arithmetic in double precision the identity above holds to machine
    precision, so the acceptance thresholds become real tests of the head rather than
    measurements of the float32 accumulation floor that R1 measured (median relative error
    1.265e-05, 0.87x the sqrt(n)*eps prediction). `intercept_f64` is the head shipped to
    Topic A; the float32 `lsqr` `intercept` head is kept as the round-1-comparable artifact.
    """
    alpha = 100 / (A.shape[1] * Ytr.shape[1])
    out = {}
    # (tag, which feature matrix, ridge kwargs). The f64 family must use features built by a
    # float64 scaler/PCA -- casting the float32 features here is what broke the identity in
    # the first run. A64/B64 are None when only the float32 families are requested.
    families = [
        ("", "f32", dict(solver="lsqr", max_iter=1000)),      # the faithful head
        ("_exact", "f32", dict(solver="cholesky")),           # exact, still float32
        ("_f64", "f64", dict(solver="cholesky")),             # exact, double precision
    ]
    if FAMILY == "f64":
        families = [f for f in families if f[0] == "_f64"]
    elif FAMILY == "f32":
        families = [f for f in families if f[1] == "f32"]
    for tag, which, kw in families:
        if which == "f64":
            assert A64 is not None, "f64 family requested without float64 features"
            Ad, Bd = A64, B64
            Yd = Ytr.astype(np.float64, copy=False)
        else:
            Ad, Bd = A.astype(np.float32, copy=False), B.astype(np.float32, copy=False)
            Yd = Ytr.astype(np.float32, copy=False)
        mu = Yd.mean(axis=0, keepdims=True)

        r = Ridge(alpha=alpha, random_state=0, fit_intercept=False, **kw).fit(Ad, Yd)
        out["nointercept" + tag] = (r.predict(Bd), r.predict(Ad))

        r = Ridge(alpha=alpha, random_state=0, fit_intercept=True, **kw).fit(Ad, Yd)
        out["intercept" + tag] = (r.predict(Bd), r.predict(Ad))

        r = Ridge(alpha=alpha, random_state=0, fit_intercept=False, **kw).fit(Ad, Yd - mu)
        out["ycentered" + tag] = (r.predict(Bd) + mu, r.predict(Ad) + mu)
    return out


def per_gene(P, Y, Ptr, Ytr, genes):
    """Faithful-way (pooled over the fold) per-gene metrics, plus training-fold means."""
    rows = []
    P = P.astype(np.float64, copy=False)
    Y = Y.astype(np.float64, copy=False)
    Ptr = Ptr.astype(np.float64, copy=False)
    Ytr = Ytr.astype(np.float64, copy=False)
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
            # Means and sds are accumulated in float64 regardless of the array's storage
            # dtype. Y is stored float32, and np.mean on a float32 array accumulates in
            # float32, which puts a ~5e-06 relative floor on the train-mean check for
            # reasons that have nothing to do with the head being tested.
            mean_pred=float(P[:, j].mean()),
            mean_target=float(Y[:, j].mean()),
            # std_pred / std_target give the scale ratio rho = s_yhat / s_y that the
            # four-rung ladder needs (oversight Decision 2). Population sd, matching the
            # SS_tot convention used for r2 above, so the identity
            # R2 = 2*r*rho - rho^2 - b^2/s_y^2 holds exactly on these columns.
            std_pred=float(P[:, j].std()),
            std_target=float(Y[:, j].std()),
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

        if FAMILY in ("all", "f32"):
            A, B = features(X[tr], X[te], dtype=np.float32)
        else:
            A = B = np.empty((0, LATENT), np.float32)
        if FAMILY in ("all", "f64"):
            A64, B64 = features(X[tr], X[te], dtype=np.float64)
        else:
            A64 = B64 = None
        preds = fit_heads(A if A.size else A64, B if B.size else B64, Y[tr], A64, B64)

        for head, (P, Ptr) in preds.items():
            for row in per_gene(P, Y[te], Ptr, Y[tr], genes):
                rows.append(dict(encoder=enc, task=task, fold=k, head=head,
                                 n_train=int(tr.sum()), n_test=int(te.sum()),
                                 n_test_samples=len(test_ids), **row))

        # max |delta| between heads' predictions, per solver family, for the acceptance checks
        rec = dict(encoder=enc, task=task, fold=k)
        for tag in [t for t in ("", "_exact", "_f64")
                    if ("intercept" + t) in preds]:
            ybar = Y[tr].astype(np.float64 if tag == "_f64" else np.float32).mean(
                axis=0, keepdims=True)
            rec[f"max_abs_intercept_minus_ycentered{tag}"] = float(
                np.max(np.abs(preds["intercept" + tag][0] - preds["ycentered" + tag][0])))
            rec[f"max_abs_intercept_minus_nointercept{tag}"] = float(
                np.max(np.abs(preds["intercept" + tag][0] - preds["nointercept" + tag][0])))
            # the shift should equal ybar exactly (see fit_heads docstring)
            rec[f"max_abs_shift_minus_ybar{tag}"] = float(np.max(np.abs(
                (preds["intercept" + tag][0] - preds["nointercept" + tag][0]) - ybar)))
        deltas.append(rec)
        # progress line reads whichever family was actually fitted
        PTAG = "" if "intercept" in preds else "_f64"
        d_ni = rec[f"max_abs_intercept_minus_nointercept{PTAG}"]
        d_yc = rec[f"max_abs_intercept_minus_ycentered{PTAG}"]

        # prediction shards: the faithful-solver intercept head and the exact-solver one,
        # distinguished by the `head` column so downstream work can choose.
        for hname in [h for h in ("intercept", "intercept_exact", "intercept_f64")
                      if h in preds]:
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
    # Suffixed by family: an f64-only corrected pass must not overwrite the float32 shards
    # written by the full pass, which remain valid.
    pq.write_table(tab, f"{PARQ}/{task}/preds__{enc}{SUF}.parquet", compression="snappy")
    print(f"[{task}] {tab.num_rows:,} rows written, {time.time()-t0:.0f}s", flush=True)
    del X, Y, R, shards

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/head_intercept__{enc}{SUF}.csv", index=False)

# ------------------------------------------------------------------- acceptance
piv = d.pivot_table(index=["task", "fold", "gene"], columns="head",
                    values=["pearson", "r2", "mean_pred", "mean_target",
                            "train_mean_pred", "train_mean_target"])
dd = pd.DataFrame(deltas)
dd.to_csv(f"{OUT}/head_deltas__{enc}{SUF}.csv", index=False)

print("\n=== R1 acceptance, by solver family ===")
print("(`lsqr` is the faithful head; `cholesky` is the exact solve. The three heads are "
      "algebraically identical up to a per-gene shift of ybar, so any deviation in the lsqr "
      "family is its iterative tolerance.)")
acc = []
# Thresholds per oversight Decision 1. The float32 families keep R1's original numbers,
# which are known to sit below the measured accumulation floor and are retained only as a
# record. The FLOAT64 family carries the real tests: under exact double-precision arithmetic
# the three-head identity must hold to machine precision, so a failure there is a bug.
THRESH = {
    "":       dict(a1=1e-6, a2=1e-4, a3=1e-6,  shift=1e-4, relative=False),
    "_exact": dict(a1=1e-6, a2=1e-4, a3=1e-6,  shift=1e-4, relative=False),
    "_f64":   dict(a1=1e-9, a2=1e-9, a3=1e-10, shift=1e-9, relative=True),
}
FAMS = [("", "lsqr float32 (faithful)"),
        ("_exact", "cholesky float32"),
        ("_f64", "cholesky float64 (Topic A head)")]
for tag, fam in [f for f in FAMS if ("pearson", "intercept" + f[0]) in piv.columns]:
    T = THRESH[tag]
    dp = (piv[("pearson", "intercept" + tag)] - piv[("pearson", "nointercept" + tag)]).abs()
    dtm = (piv[("train_mean_pred", "intercept" + tag)]
           - piv[("train_mean_target", "intercept" + tag)]).abs()
    # A3 is stated as a RELATIVE error for the float64 family, per Decision 1.
    if T["relative"]:
        dtm = dtm / piv[("train_mean_target", "intercept" + tag)].abs()
    a1, a2 = float(dp.max()), float(dd[f"max_abs_intercept_minus_ycentered{tag}"].max())
    a3 = float(dtm.max())
    a_shift = float(dd[f"max_abs_shift_minus_ybar{tag}"].max())
    unit = " (relative)" if T["relative"] else ""
    for name, val, thr in (("A1 max|dPearson(int-noint)|", a1, T["a1"]),
                           ("A2 max|pred(int)-pred(ycent)|", a2, T["a2"]),
                           (f"A3 max|train mean pred - target|{unit}", a3, T["a3"]),
                           ("A2b max|(int-noint) - ybar|", a_shift, T["shift"])):
        acc.append(dict(encoder=enc, solver=fam, check=name, value=val,
                        threshold=thr, passed=bool(val < thr),
                        is_hard_stop=bool(tag == "_f64")))
        print(f"  {fam:<34} {name:<44} = {val:.3e}  [thr {thr:.0e}]  "
              f"{'PASS' if val < thr else 'FAIL'}")
accdf = pd.DataFrame(acc)
accdf.to_csv(f"{OUT}/acceptance__{enc}{SUF}.csv", index=False)

# Oversight Decision 1: a float64 identity failure is a bug, not a floor, and stops the run.
f64_fail = accdf[accdf.is_hard_stop & ~accdf.passed]
if len(f64_fail):
    print("\n*** STOP-AND-REPORT: float64 identity failure ***", flush=True)
    print(f64_fail.to_string(index=False), flush=True)

# ------------------------------------------------- solver sensitivity (Decision 1, last para)
# Under exact arithmetic the intercept and nointercept solutions are identical, so the whole
# lsqr-vs-cholesky gap is solver non-convergence in one or both fits. Quantify how much
# solver noise an individual per-gene Pearson in the faithful protocol carries.
have_f32 = all(("pearson", h) in piv.columns for h in ("nointercept", "nointercept_exact"))
if not have_f32:
    print("\n[solver sensitivity] skipped: needs both float32 families")
ss = ((piv[("pearson", "nointercept")] - piv[("pearson", "nointercept_exact")]).abs()
      if have_f32 else None)
if have_f32:
    ss = ss.reset_index().rename(columns={0: "abs_dpearson"})
    ss.columns = ["task", "fold", "gene", "abs_dpearson"]
    sens = (ss.groupby("task")["abs_dpearson"].agg(["mean", "max", "count"])
              .rename(columns={"mean": "mean_abs_dpearson", "max": "max_abs_dpearson"}))
    sens["encoder"] = enc
    sens["verdict"] = np.where(sens.mean_abs_dpearson > 5e-3, "known-limitation",
                        np.where(sens.mean_abs_dpearson <= 1e-3, "footnote", "between"))
    sens.to_csv(f"{OUT}/solver_sensitivity__{enc}{SUF}.csv")
    print("\n=== solver sensitivity, nointercept head in float32, |Pearson(lsqr)-Pearson(cholesky)| ===")
    print(sens.round(6).to_string())

# A5: the `nointercept` control must reproduce round 1's faithful pca_ridge per-task Pearson.
# This is the check that actually establishes the pipeline is the faithful one.
rt_path = f"{ROOT}/results/summary/results_task.csv"
if os.path.exists(rt_path):
    rt = pd.read_csv(rt_path)
    rt = rt[(rt["head"] == "pca_ridge") & (rt["encoder"] == enc)][["task", "pearson_mean"]]
    ANCHOR = "nointercept" if (d["head"] == "nointercept").any() else "nointercept_f64"
    ours = (d[d["head"] == ANCHOR].groupby(["task", "fold"])["pearson"].mean()
              .groupby("task").mean().rename("ours").reset_index())
    cmp = ours.merge(rt, on="task", how="outer")
    cmp["abs_diff"] = (cmp["ours"] - cmp["pearson_mean"]).abs()
    cmp.to_csv(f"{OUT}/faithful_check__{enc}{SUF}.csv", index=False)
    print(f"A5 nointercept vs round-1 faithful pca_ridge, per task: "
          f"max |diff| = {cmp['abs_diff'].max():.3e}, mean {cmp['abs_diff'].mean():.3e} "
          f"over {cmp['abs_diff'].notna().sum()} tasks   [expect < 1e-3]  "
          f"{'PASS' if cmp['abs_diff'].max() < 1e-3 else 'FAIL'}")
    print(cmp.round(5).to_string(index=False))
else:
    print(f"A5 SKIPPED: {rt_path} absent")

fm = d.groupby(["task", "fold", "head"])["r2"].median().reset_index()
fp = fm.pivot_table(index=["task", "fold"], columns="head", values="r2")
print("A4 fold-median R^2 > 0, by head: " + "  ".join(
    f"{h} {int((fp[h] > 0).sum())}/{len(fp)}" for h in fp.columns))
print("\nfold-median R^2 by task (mean over folds):")
print(fp.groupby(level=0).mean().round(4).to_string())
PRIMARY = "intercept" if (d["head"] == "intercept").any() else "intercept_f64"
print(f"\nmean Pearson by task ({PRIMARY} head, faithful pooled metric):")
print(d[d["head"] == PRIMARY].groupby("task")["pearson"].mean().round(4).to_string())

with open(f"{OUT}/PROVENANCE__{enc}{SUF}.txt", "w") as f:
    f.write(
        f"Round 2, stage R1b - intercept refit incl. float64 head, encoder {enc}\n"
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
