#!/usr/bin/env python
"""Spot-bootstrap 95% intervals for theta1 on the four IDC slides.

Stage: R6 (deck_figures_and_repo_update.md section 1.2, fig07 -- "if bootstrap
intervals are not already in results/round2/R6_theta/, compute them (200
resamples) from the morphology and count parquets and commit the CSV").

Inputs:  instrumentation/morphology_v2/IDC_morph.parquet   per-spot morphology
         bench_data/IDC/adata/*.h5ad                       raw counts
         bench_data/IDC/var_50genes.json                   target gene list
Outputs: results/round2/R6_theta/r6_theta_bootstrap_ci.csv

theta1 is Pearson(mean neoplastic nuclear area, raw GATA3 counts) over a slide's
spots, as defined in round2_r6_theta.py. That script already draws 200 spot
bootstrap resamples to form `se_hat_raw`; what the repository lacks is the
interval, so this recomputes the same resamples and takes percentiles as well.

round2_r6_theta.py cannot be imported -- it runs its whole analysis at module
level -- so `pearson_nan` and the resampling are reproduced here rather than
reused. That is a risk (two copies of one estimator can drift), so it is checked
rather than asserted: the bootstrap SD computed here must match the committed
`se_hat_raw` in theta_by_slide.parquet for all four slides, or this script
fails. Same seed (1) and same resample shape, so the match should be exact.

Both percentile and normal-approximation intervals are written. The figure uses
the percentile interval; the normal one is there because it is what a reader who
only has `se_hat_raw` would construct, and the two differ when the bootstrap
distribution is skewed, which it is for a correlation near zero.
"""
import glob
import json
import os
import sys
import time

import anndata as ad
import numpy as np
import pandas as pd

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
MORPH = f"{ROOT}/instrumentation/morphology_v2"
BD = f"{ROOT}/bench_data"
OUT = f"{ROOT}/results/round2/R6_theta"

TASK, GENE = "IDC", "GATA3"
SEED, N_BOOT = 1, 200          # identical to round2_r6_theta.py
MIN_SPOTS = 500


def pearson_nan(a, b):
    """Pearson that returns nan rather than raising on a degenerate input.

    Reproduced from round2_r6_theta.py; see the module docstring on why it is
    copied rather than imported, and on the check that keeps the two in step.
    """
    if len(a) < 3:
        return np.nan
    sa, sb = a.std(), b.std()
    if not np.isfinite(sa) or not np.isfinite(sb) or sa == 0 or sb == 0:
        return np.nan
    return float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb))


M = pd.read_parquet(f"{MORPH}/{TASK}_morph.parquet")
with open(f"{BD}/{TASK}/var_50genes.json") as f:
    genes = json.load(f)
genes = genes["genes"] if isinstance(genes, dict) else list(genes)
assert GENE in genes, f"{GENE} is not in {TASK}'s target list"

frames = []
for p in sorted(glob.glob(f"{BD}/{TASK}/adata/*.h5ad")):
    sid = os.path.basename(p)[:-5]
    A = ad.read_h5ad(p)
    if GENE not in set(map(str, A.var_names)):
        print(f"[skip] {sid}: {GENE} absent from its panel")
        continue
    sub = A[:, [GENE]]
    Xc = np.asarray(sub.X.todense() if hasattr(sub.X, "todense") else sub.X, dtype=np.float64)
    frames.append(pd.DataFrame(Xc, columns=[GENE]).assign(
        sample_id=sid, barcode=np.asarray(A.obs_names).astype(str)))
    del A
assert frames, f"no sample measures {GENE}"
C = pd.concat(frames, ignore_index=True)
D = M.merge(C, on=["sample_id", "barcode"], how="inner")
print(f"joined {len(D):,} spots over {D.sample_id.nunique()} slides")

ref = pd.read_parquet(f"{OUT}/theta_by_slide.parquet")
ref = ref[(ref.task == TASK) & (ref.gene == GENE)].set_index("sample_id")

rows = []
for sid, g in D.groupby("sample_id"):
    area = g.neo_area_mean.astype(float).to_numpy()
    y = g[GENE].astype(float).to_numpy()
    m = np.isfinite(area) & np.isfinite(y)
    a_, y_ = area[m], y[m]
    if len(a_) < MIN_SPOTS:
        print(f"[skip] {sid}: {len(a_)} usable spots below the {MIN_SPOTS} minimum")
        continue

    point = pearson_nan(a_, y_)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(a_), size=(N_BOOT, len(a_)))
    vals = np.array([pearson_nan(a_[i], y_[i]) for i in idx])
    vals = vals[np.isfinite(vals)]
    lo, hi = np.percentile(vals, [2.5, 97.5])
    sd = float(vals.std(ddof=1))

    rows.append(dict(task=TASK, gene=GENE, sample_id=sid, n_spots=int(len(a_)),
                     theta1_raw=point, boot_sd=sd,
                     ci_lo_percentile=float(lo), ci_hi_percentile=float(hi),
                     ci_lo_normal=point - 1.96 * sd, ci_hi_normal=point + 1.96 * sd,
                     n_boot=int(len(vals)), seed=SEED,
                     se_hat_raw_committed=float(ref.loc[sid, "se_hat_raw"]),
                     theta1_raw_committed=float(ref.loc[sid, "r_hat_raw"])))

B = pd.DataFrame(rows).sort_values("theta1_raw", ascending=False)

# The estimator check. If either of these fails, the copied Pearson or the
# resampling has drifted from round2_r6_theta.py and the intervals are not
# intervals for the committed point estimates.
d_point = (B.theta1_raw - B.theta1_raw_committed).abs().max()
d_se = (B.boot_sd - B.se_hat_raw_committed).abs().max()
print(f"point estimate reproduction: max |delta| {d_point:.3e}")
print(f"bootstrap SD reproduction:   max |delta| {d_se:.3e}")
assert d_point < 1e-9, f"theta1 does not reproduce (max delta {d_point:.3e})"
assert d_se < 1e-9, f"bootstrap SD does not reproduce (max delta {d_se:.3e})"

B.round(8).to_csv(f"{OUT}/r6_theta_bootstrap_ci.csv", index=False)
with open(f"{OUT}/PROVENANCE__r6_theta_bootstrap_ci.txt", "w") as f:
    f.write("Round 2 R6 - spot-bootstrap 95% intervals for theta1\n"
            f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'NA')}\n"
            f"node            : {os.environ.get('SLURMD_NODENAME', 'NA')}\n"
            f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
            "script          : code/scripts/build_r6_theta_bootstrap.py\n"
            f"command_line    : {' '.join(sys.argv)}\n"
            f"task/gene       : {TASK}/{GENE}\n"
            f"seed/n_boot     : {SEED}/{N_BOOT}\n"
            f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
            "estimand        : Pearson(neo_area_mean, raw counts) per slide\n"
            "estimator_check : bootstrap SD reproduces se_hat_raw in\n"
            f"                  theta_by_slide.parquet to {d_se:.1e}; point estimate to {d_point:.1e}\n"
            "plan            : deck_figures_and_repo_update.md section 1.2 fig07\n")

print()
print(B[["sample_id", "n_spots", "theta1_raw", "ci_lo_percentile", "ci_hi_percentile",
         "boot_sd"]].round(4).to_string(index=False))
