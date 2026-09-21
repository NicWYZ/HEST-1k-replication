#!/usr/bin/env python
"""Round 2, stage R6: slide-level estimands for Topic B.

Stage: R6, the slide-level estimand theta1 (round2_R5_decisions.md directive 2.4).

Three parts, per the plan.

1. theta1 per slide. For each task, each of its 50 target genes, and each slide with at
   least 500 spots carrying at least one neoplastic nucleus:
       r_hat(s,g) = Pearson( mean neoplastic nuclear area , log(1+y_g) ) over that slide's
                    qualifying spots
   with a spot bootstrap (200 resamples) giving the within-slide sampling standard error
   sigma_hat(s,g). Computed on log1p counts AND on raw counts, since round 1 found the raw
   version matched the paper's own figure more closely.
   ACCEPTANCE: for IDC and GATA3, r_hat on NCBI785 reproduces 0.410577 (log1p) and
   0.420947 (raw) to 1e-3, the values on the morphology_v2 build this script reads.
   Round 1's 0.458 was computed on the superseded morphology build and is retained as
   a historical value only; see the acceptance block for why they differ.

2. Variance components. Per (task, gene), method-of-moments between-slide variance
       tau2_hat(g) = max(0, Var_s(r_hat(s,g)) - mean_s(sigma_hat^2(s,g)))
   and the ratio tau2_hat(g) / mean_s(sigma_hat^2(s,g)). A ratio well above 1 means slide
   heterogeneity dominates spot-level sampling noise, which is Topic B's premise.
   Also theta2 where defined: the difference in mean log(1+y_g) between spots with
   neoplastic fraction above 0.7 and below 0.3, per slide, with the same bootstrap and
   variance components.

3. Nuclear area against resolution. Per-slide median and IQR of neoplastic nuclear area
   joined to pixel size, with the within-task Spearman correlation between slide-level
   median area and pixel size. If area moves with resolution among slides of the same task,
   CellViT's segmentation is resolution-dependent and these covariates need a correction
   before they carry any Topic B conclusion.

Usage: round2_r6_theta.py [task ...]      (default: every task with a morphology parquet)
"""
import glob
import json
import os
import sys
import time
import zlib

import anndata as ad
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.stats import spearmanr


def config_hash(*parts):
    """Stable across processes and Python versions.

    NOT `hash()`: Python randomises str hashing per process unless PYTHONHASHSEED is
    set, so a config_hash over anything containing a string identified nothing — it
    differed on every run, which defeats the point of recording it in PROVENANCE.
    """
    return zlib.crc32(repr(parts).encode()) & 0xFFFFFFFF

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD = f"{ROOT}/bench_data"
MORPH = f"{ROOT}/instrumentation/morphology_v2"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"
OUT = f"{ROOT}/results/round2/R6_theta"

SEED = 1
N_BOOT = 200
MIN_SPOTS = 500          # per-slide minimum, spots with >=1 neoplastic nucleus
NEO_HI, NEO_LO = 0.7, 0.3


def pearson_nan(a, b):
    """Pearson that returns nan rather than raising on a degenerate input."""
    if len(a) < 3:
        return np.nan
    sa, sb = a.std(), b.std()
    if not np.isfinite(sa) or not np.isfinite(sb) or sa == 0 or sb == 0:
        return np.nan
    return float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb))


def boot_se(a, b, n_boot=N_BOOT, seed=SEED):
    """Spot-bootstrap standard error of the Pearson correlation."""
    n = len(a)
    if n < 3:
        return np.nan
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    vals = np.array([pearson_nan(a[i], b[i]) for i in idx])
    vals = vals[np.isfinite(vals)]
    return float(vals.std(ddof=1)) if len(vals) > 2 else np.nan


def boot_se_diff(y, hi, lo, n_boot=N_BOOT, seed=SEED):
    """Spot-bootstrap standard error of the theta2 mean difference."""
    if hi.sum() < 10 or lo.sum() < 10:
        return np.nan
    rng = np.random.default_rng(seed)
    yh, yl = y[hi], y[lo]
    vals = np.array([yh[rng.integers(0, len(yh), len(yh))].mean()
                     - yl[rng.integers(0, len(yl), len(yl))].mean()
                     for _ in range(n_boot)])
    return float(vals.std(ddof=1))


def load_task(task):
    """Per-spot morphology joined to raw counts for the task's 50 target genes."""
    M = pd.read_parquet(f"{MORPH}/{task}_morph.parquet")
    with open(f"{BD}/{task}/var_50genes.json") as f:
        genes = json.load(f)
    genes = genes["genes"] if isinstance(genes, dict) else list(genes)

    frames = []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        A = ad.read_h5ad(p)
        have = [g for g in genes if g in set(map(str, A.var_names))]
        if not have:
            continue
        sub = A[:, have]
        Xc = np.asarray(sub.X.todense() if hasattr(sub.X, "todense") else sub.X, dtype=np.float64)
        frames.append(pd.DataFrame(Xc, columns=have).assign(
            sample_id=sid, barcode=np.asarray(A.obs_names).astype(str)))
        del A
    if not frames:
        return None, None, genes
    C = pd.concat(frames, ignore_index=True)
    D = M.merge(C, on=["sample_id", "barcode"], how="inner")
    return D, [g for g in genes if g in D.columns], genes


meta = pd.read_csv(META)
SID = "sample_id" if "sample_id" in meta.columns else meta.columns[0]
PX = "pixel_size_um" if "pixel_size_um" in meta.columns else "pixel_size_um_estimated"
TASKC = next(c for c in meta.columns if c.lower() == "task")
px_of = {(t, str(s)): float(v) for t, s, v in zip(meta[TASKC], meta[SID], meta[PX])}

os.makedirs(OUT, exist_ok=True)
tasks = sys.argv[1:] or sorted(os.path.basename(f).replace("_morph.parquet", "")
                               for f in glob.glob(f"{MORPH}/*_morph.parquet"))

theta_rows, area_rows = [], []
for task in tasks:
    t0 = time.time()
    D, genes, genes_all = load_task(task)
    if D is None or not genes:
        print(f"[skip] {task}: no gene columns after join", flush=True)
        continue
    D = D[D.n_neoplastic.fillna(0) >= 1]
    counts = D.groupby("sample_id").size()
    ok_slides = sorted(counts[counts >= MIN_SPOTS].index)
    print(f"\n[{task}] {len(D):,} spots with >=1 neoplastic nucleus, "
          f"{len(ok_slides)}/{D.sample_id.nunique()} slides pass the {MIN_SPOTS}-spot minimum, "
          f"{len(genes)}/{len(genes_all)} target genes present", flush=True)

    # --- part 3: nuclear area against resolution (needs only the morphology columns)
    for s, g_ in D.groupby("sample_id"):
        a = g_.neo_area_mean.astype(float).dropna().to_numpy()
        if len(a) < 50:
            continue
        area_rows.append(dict(task=task, sample_id=s, n_spots=len(a),
                              area_median=float(np.median(a)),
                              area_q25=float(np.percentile(a, 25)),
                              area_q75=float(np.percentile(a, 75)),
                              pixel_size_um=px_of.get((task, s), np.nan)))

    for s in ok_slides:
        g_ = D[D.sample_id == s]
        area = g_.neo_area_mean.astype(float).to_numpy()
        neo_frac = g_.frac_neoplastic.astype(float).to_numpy()
        fin = np.isfinite(area)
        for gene in genes:
            y_raw = g_[gene].astype(float).to_numpy()
            m = fin & np.isfinite(y_raw)
            if m.sum() < MIN_SPOTS:
                continue
            a_, yr = area[m], y_raw[m]
            yl = np.log1p(yr)
            rec = dict(task=task, sample_id=s, gene=gene, n_spots=int(m.sum()),
                       pixel_size_um=px_of.get((task, s), np.nan),
                       r_hat=pearson_nan(a_, yl),
                       se_hat=boot_se(a_, yl),
                       r_hat_raw=pearson_nan(a_, yr),
                       se_hat_raw=boot_se(a_, yr))
            # theta2: mean log1p difference between neoplastic-rich and neoplastic-poor spots
            hi, lo = neo_frac[m] > NEO_HI, neo_frac[m] < NEO_LO
            if hi.sum() >= 10 and lo.sum() >= 10:
                rec.update(theta2=float(yl[hi].mean() - yl[lo].mean()),
                           theta2_se=boot_se_diff(yl, hi, lo),
                           n_hi=int(hi.sum()), n_lo=int(lo.sum()))
            else:
                rec.update(theta2=np.nan, theta2_se=np.nan,
                           n_hi=int(hi.sum()), n_lo=int(lo.sum()))
            theta_rows.append(rec)
    print(f"[{task}] done in {time.time()-t0:.0f}s", flush=True)
    del D

TH = pd.DataFrame(theta_rows)
TH_SCHEMA = pa.schema([("task", pa.string()), ("sample_id", pa.string()), ("gene", pa.string()),
                       ("n_spots", pa.int32()), ("pixel_size_um", pa.float64()),
                       ("r_hat", pa.float64()), ("se_hat", pa.float64()),
                       ("r_hat_raw", pa.float64()), ("se_hat_raw", pa.float64()),
                       ("theta2", pa.float64()), ("theta2_se", pa.float64()),
                       ("n_hi", pa.int32()), ("n_lo", pa.int32())])
for cc in ("task", "sample_id", "gene"):
    TH[cc] = TH[cc].astype(str)
for cc in ("n_spots", "n_hi", "n_lo"):
    TH[cc] = TH[cc].astype("int32")
pq.write_table(pa.Table.from_pandas(TH[[f.name for f in TH_SCHEMA]], schema=TH_SCHEMA,
                                    preserve_index=False),
               f"{OUT}/theta_by_slide.parquet", compression="snappy")
print(f"\n[theta] {len(TH):,} (slide, gene) rows -> theta_by_slide.parquet")

# ---------------------------------------------------------------- acceptance check
# Restated against morphology_v2 per the closeout memo section 1.3. Round 1's 0.458 was
# computed on instrumentation/morphology, the earlier CellViT build; this script reads
# morphology_v2, which detects ~60% more neoplastic nuclei per spot and qualifies 2,195
# spots for this cell against v1's 1,980, so the same computation on different inputs
# gives a different number. That is not a reproduction failure: run against v1 this code
# returns 0.457791, matching round 1 to six decimals (r6_theta_build_comparison.csv), and
# the substantive finding is unchanged -- the rank order across the four IDC slides is
# identical and the between-slide spread is 0.4859 (v2) against 0.5058 (v1).
ACCEPT = {"r_hat": (0.410577, "log1p"), "r_hat_raw": (0.420947, "raw counts")}
ACCEPT_TOL = 1e-3
HISTORICAL_V1_RAW = 0.457791   # round 1's value, on the superseded morphology build

acc = TH[(TH.task == "IDC") & (TH.gene == "GATA3") & (TH.sample_id == "NCBI785")]
if len(acc):
    for col, (ref, lab) in ACCEPT.items():
        v = float(acc[col].iloc[0])
        print(f"ACCEPTANCE IDC/GATA3/NCBI785 ({lab}): {v:.6f} against morphology_v2's "
              f"{ref:.6f} -> |diff| {abs(v-ref):.2e} "
              f"{'PASS' if abs(v-ref) < ACCEPT_TOL else 'FAIL'}")
    print(f"  (historical: round 1 reported {HISTORICAL_V1_RAW:.6f} on the v1 morphology "
          f"build; the difference is the build, not the computation)")
else:
    print("ACCEPTANCE IDC/GATA3/NCBI785: row absent -- reporting as not reproduced")

# ---------------------------------------------------------------- variance components
vc = []
for (task, gene), g_ in TH.groupby(["task", "gene"]):
    for est, se in (("r_hat", "se_hat"), ("r_hat_raw", "se_hat_raw"), ("theta2", "theta2_se")):
        v = g_[[est, se]].dropna()
        if len(v) < 3:
            continue
        var_between = float(v[est].var(ddof=1))
        mean_within = float((v[se] ** 2).mean())
        tau2 = max(0.0, var_between - mean_within)
        vc.append(dict(task=task, gene=gene, estimand=est, n_slides=len(v),
                       var_between_raw=var_between, mean_within_var=mean_within,
                       tau2_hat=tau2,
                       ratio=tau2 / mean_within if mean_within > 0 else np.nan,
                       mean_estimate=float(v[est].mean())))
VC = pd.DataFrame(vc)
VC.to_csv(f"{OUT}/variance_components.csv", index=False)
print(f"[vc] {len(VC)} (task, gene, estimand) rows -> variance_components.csv")
for est, g_ in VC.groupby("estimand"):
    q = g_.ratio.describe(percentiles=[.25, .5, .75])
    print(f"  {est:<11} tasks {g_.task.nunique():2d}  genes {len(g_):4d}  "
          f"ratio median {q['50%']:.2f}  IQR [{q['25%']:.2f}, {q['75%']:.2f}]  "
          f"frac>1 {(g_.ratio > 1).mean():.2f}")
nt = VC.groupby("task").apply(lambda g: g.n_slides.max() >= 3, include_groups=False)
print(f"  tasks with >=3 qualifying slides: {int(nt.sum())}/{len(nt)} "
      f"({sorted(nt[nt].index)})")

# ---------------------------------------------------------------- area against resolution
AR = pd.DataFrame(area_rows)
AR.to_csv(f"{OUT}/nuclear_area_by_resolution.csv", index=False)
rows = []
for task, g_ in AR.groupby("task"):
    v = g_[["area_median", "pixel_size_um"]].dropna()
    if v.pixel_size_um.nunique() < 3:
        rows.append(dict(task=task, n_slides=len(v), distinct_px=int(v.pixel_size_um.nunique()),
                         spearman=np.nan, p=np.nan,
                         note="fewer than 3 distinct pixel sizes; correlation undefined"))
        continue
    rho, pv = spearmanr(v.area_median, v.pixel_size_um)
    rows.append(dict(task=task, n_slides=len(v), distinct_px=int(v.pixel_size_um.nunique()),
                     spearman=float(rho), p=float(pv), note=""))
AC = pd.DataFrame(rows)
AC.to_csv(f"{OUT}/area_resolution_correlation.csv", index=False)
print("\n=== slide-level median neoplastic nuclear area against pixel size ===")
print(AC.round(4).to_string(index=False))

with open(f"{OUT}/PROVENANCE.txt", "w") as f:
    f.write(
        f"Round 2, stage R6 - slide-level estimands\n"
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
        f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
        f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
        f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
        f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
        f"script          : code/scripts/round2_r6_theta.py\n"
        f"command_line    : {' '.join(sys.argv)}\n"
        f"tasks           : {tasks}\n"
        f"seed/n_boot/min_spots/neo_hi/neo_lo : {SEED}/{N_BOOT}/{MIN_SPOTS}/{NEO_HI}/{NEO_LO}\n"
        f"config_hash     : {config_hash(SEED, N_BOOT, MIN_SPOTS, NEO_HI, NEO_LO):08x}\n"
        "plan            : round2_execution_plan.md stage R6 / plan phase R6\n")
