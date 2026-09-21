#!/usr/bin/env python
"""Build results/round2/R1b_heads/r1b_ladder_by_encoder.csv (and the pooled row).

Stage: R1b, four-rung R2 ladder (round2_R1_decisions.md Decision 2).
Memo clause: deck_figures_and_repo_update.md section 1.2 fig05 -- "if the latter
is not in the repository, compute it from head_intercept__*__f64.csv and commit it".

Inputs:  results/round2/R1b_heads/head_intercept__<encoder>.csv      (float32 families)
         results/round2/R1b_heads/head_intercept__<encoder>__f64.csv  (float64 family)
Outputs: results/round2/R1b_heads/r1b_ladder_by_encoder.csv
         results/round2/R1b_heads/r1b_ladder_pooled.csv

Why both files. fig05 needs two things the repository did not carry: the rho/r
ratio per encoder for its inset, and the POOLED rungs for its left panel. The
pooled rungs are not the mean of r1b_ladder_by_task.csv's columns -- that gives
-1.064 / -0.189 / +0.077 / +0.167, because averaging ten task medians is not the
median over all cells. The pooled figures the R8 report quotes (-0.9532,
-0.1552, +0.0301, +0.0997) are medians over every encoder-task-fold-gene row, so
they have to be recomputed from the per-gene files rather than derived.

Methodology is not reimplemented here: this imports `ladder()` from
round2_r1b_ladder.py, the script that produced r1b_ladder_by_task.csv, and calls
it per encoder and once over everything. The two files are therefore consistent
with the by-task file by construction rather than by inspection -- and that is
then verified: the script also rebuilds the by-task table and compares it to the
committed r1b_ladder_by_task.csv, failing if any cell moves.

Note on inputs. The memo names head_intercept__*__f64.csv and that is correct,
though not for the reason the rung names suggest. `ladder()` keys its first two
rungs on the head names `nointercept` and `intercept`, which in the unsuffixed
files are the float32 arms -- so a first attempt here read the float32 files for
those two rungs. That does not reproduce the committed r1b_ladder_by_task.csv:
its `faithful` column differs by up to 9.2e-03. Testing each candidate head
against the committed column settles it -- `faithful` reproduces to 2.2e-16 from
`nointercept_f64` and `train-mean intercept` to 8.3e-17 from `intercept_f64`.
The committed ladder is the FLOAT64 ladder on all four rungs.

So only the __f64 files are read, with the `_f64` suffix stripped from the head
names so that `ladder()` finds them under the names it expects. Two traps avoided
by doing it this way: the unsuffixed files still contain the SUPERSEDED float64
arm from R1b's first pass (built on float32-derived features, the bug that made
the identity thresholds fail), so concatenating both files would silently give
two different `intercept_f64` arms per cell -- the R2 identity degrades from
4.1e-11 to 7.8e-03 when that happens, which is how it was caught.
"""
import glob
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from round2_r1b_ladder import identity_check, ladder  # noqa: E402

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
IN = f"{ROOT}/results/round2/R1b_heads"
RUNGS = ["faithful", "train-mean intercept", "oracle level",
         "oracle level and optimal scale"]

files = sorted(glob.glob(f"{IN}/head_intercept__*__f64.csv"))
assert files, f"no float64 head metrics under {IN}"
D = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
D = D[D["head"].str.endswith("_f64")].copy()
D["head"] = D["head"].str.removesuffix("_f64")
print(f"loaded {len(files)} float64 files -> {len(D):,} rows, {D.encoder.nunique()} encoders, "
      f"heads {sorted(D['head'].unique())}")
dup = D.groupby(["encoder", "task", "fold", "gene", "head"]).size().max()
assert dup == 1, f"duplicated cells (max {dup})"
for h in ("nointercept", "intercept"):
    assert (D["head"] == h).any(), f"head {h} missing -- ladder() cannot build its rungs"

med, mx = identity_check(D[D["head"] == "intercept"])
print(f"identity check |R2_reconstructed - R2_stored|: median {med:.3e} max {mx:.3e}")
assert mx < 1e-6, f"the R2 identity does not hold on the stored columns (max {mx:.3e})"

# Reproduce the committed by-task table first. If this does not match, the
# per-encoder and pooled files below are not comparable to it and must not ship.
ref_path = f"{IN}/r1b_ladder_by_task.csv"
if os.path.exists(ref_path):
    ref = pd.read_csv(ref_path).set_index("task")
    rep = []
    for task, g in D.groupby("task"):
        rungs, rho, r = ladder(g)
        rep.append({"task": task, **{k: rungs[k] for k in RUNGS},
                    "median_rho": rho, "median_r": r})
    rep = pd.DataFrame(rep).set_index("task")
    cols = [c for c in RUNGS + ["median_rho", "median_r"] if c in ref.columns]
    delta = (rep[cols] - ref.loc[rep.index, cols]).abs().max().max()
    print(f"by-task reproduction: max |delta| over {len(rep)} tasks x {len(cols)} cols = {delta:.3e}")
    assert delta < 1e-6, f"by-task table does not reproduce (max delta {delta:.3e})"
else:
    print(f"WARNING: {ref_path} absent, cannot verify against the committed by-task table")

rows = []
for enc, g in D.groupby("encoder"):
    rungs, rho, r = ladder(g)
    rows.append({"encoder": enc, **{k: rungs[k] for k in RUNGS},
                 "median_rho": rho, "median_r": r, "rho_over_r": rho / r,
                 "n_tasks": g.task.nunique(), "n_folds": g.groupby(["task", "fold"]).ngroups})
by_enc = pd.DataFrame(rows).sort_values("oracle level and optimal scale", ascending=False)
for i in range(len(RUNGS) - 1):
    by_enc[f"gain_{i + 1}"] = by_enc[RUNGS[i + 1]] - by_enc[RUNGS[i]]
by_enc.round(6).to_csv(f"{IN}/r1b_ladder_by_encoder.csv", index=False)

rungs, rho, r = ladder(D)
pooled = pd.DataFrame([{"scope": "pooled over all encoders, tasks, folds and genes",
                        **{k: rungs[k] for k in RUNGS},
                        "median_rho": rho, "median_r": r, "rho_over_r": rho / r,
                        "n_encoders": D.encoder.nunique(), "n_tasks": D.task.nunique(),
                        "n_rows": len(D)}])
for i in range(len(RUNGS) - 1):
    pooled[f"gain_{i + 1}"] = pooled[RUNGS[i + 1]] - pooled[RUNGS[i]]
pooled.round(6).to_csv(f"{IN}/r1b_ladder_pooled.csv", index=False)

with open(f"{IN}/PROVENANCE__r1b_ladder_by_encoder.txt", "w") as f:
    f.write("Round 2 R1b - ladder by encoder and pooled\n"
            f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'NA')}\n"
            f"node            : {os.environ.get('SLURMD_NODENAME', 'NA')}\n"
            f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
            "script          : code/scripts/build_r1b_ladder_by_encoder.py\n"
            "methodology     : imports ladder() from code/scripts/round2_r1b_ladder.py, the\n"
            "                  script that produced r1b_ladder_by_task.csv, so the three files\n"
            "                  are consistent by construction\n"
            f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
            f"inputs          : {len(files)} x head_intercept__<encoder>__f64.csv\n"
            f"identity_check  : median {med:.3e} max {mx:.3e}\n"
            "plan            : deck_figures_and_repo_update.md section 1.2 fig05\n")

print("\npooled rungs:")
print(pooled[RUNGS + ["median_rho", "median_r", "rho_over_r"]].round(4).to_string(index=False))
print("\ngains:", [round(float(pooled[f'gain_{i + 1}'].iloc[0]), 4) for i in range(3)])
print("\nby encoder:")
print(by_enc[["encoder"] + RUNGS + ["rho_over_r"]].round(4).to_string(index=False))
