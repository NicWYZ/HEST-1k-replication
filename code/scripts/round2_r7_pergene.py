#!/usr/bin/env python
"""Round 2, stage R7: per-gene decomposition, joined to the donor-level variance.

Stage: R7, the per-gene decomposition (round2_R5_decisions.md directive 2.5).

Directive 2.4 changes two things from the original R7 spec:
  - the join to R6 uses the BETWEEN-DONOR variance, not between-patient, because the R5b
    audit showed HEST's patient field merges donors in COAD and splits one in IDC;
  - the per-gene replicate leak from R5c (IDC and READ) is an additional input.

Per gene, per task, this assembles:
  split terms      from R3's per-gene parquets: random - patient, blocked - patient, and
                   the novel-slide and same-patient terms where the design supports them
  replicate leak   from R5c: with_replicate - without_replicate, IDC and READ only
  donor variance   from R6: frac_donor, var_donor, var_slide, var_spot
and reports the Spearman correlations between them.

The question directive 2.4 poses is whether the genes that lose most from a
patient-respecting split are the genes with most between-donor variance. If they are, the
split penalty is explained by donor-level biological heterogeneity; if not, something else
drives it.

PRAD caveat carried into the output: R4 showed PRAD's two scan sessions are separable at
0.977 in the image features, so a per-gene novel-slide term on PRAD is partly a per-session
term. R6 then showed the session contributes no measurable EXPRESSION variance, so the
caveat applies to the features and the model, not to the targets -- both facts are recorded
in the notes column rather than left to the reader.

Usage: round2_r7_pergene.py
"""
import glob
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = "/work/users/w/e/weiyang/hest_replication"
R3 = f"{ROOT}/results/round2/R3_splits"
R6 = f"{ROOT}/results/round2/R6_variance"
OUT = f"{ROOT}/results/round2/R7_pergene"
os.makedirs(OUT, exist_ok=True)

pg = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f"{R3}/pergene__*.parquet"))
                if "replicate_leak" not in f], ignore_index=True)
print(f"[in] R3 per-gene: {len(pg):,} rows, designs {sorted(pg.design.unique())}, "
      f"encoders {sorted(pg.encoder.unique())}")

# average over folds, repeats, grids and slides -> one value per (encoder, task, design, gene)
cell = pg.groupby(["encoder", "task", "design", "gene"]).pearson.mean().unstack("design")
need = [c for c in ("random", "patient", "blocked", "blocked_buffered", "slide_out") if c in cell]
print(f"[in] designs available per gene: {need}")
T = pd.DataFrame(index=cell.index)
T["random_minus_patient"] = cell["random"] - cell["patient"]
T["blocked_minus_patient"] = cell["blocked"] - cell["patient"]
if "slide_out" in cell:
    T["novel_slide"] = cell["random"] - cell["slide_out"]
    T["same_patient_other_slide"] = cell["slide_out"] - cell["patient"]
T = T.reset_index()

# replicate leak per gene, from R5c
rl = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f"{R3}/pergene_replicate_leak__*.parquet"))],
               ignore_index=True)
rlc = (rl.groupby(["encoder", "task", "gene", "design"]).pearson.mean().unstack("design"))
rlc["replicate_leak"] = rlc["with_replicate"] - rlc["without_replicate"]
T = T.merge(rlc[["replicate_leak"]].reset_index(), on=["encoder", "task", "gene"], how="left")
print(f"[in] replicate leak joined for {int(T.replicate_leak.notna().sum())} gene-encoder rows "
      f"({sorted(rl.task.unique())})")

# donor-level variance from R6 (encoder-independent: it is a property of the expression)
V = pd.read_csv(f"{R6}/donor_variance_components.csv")
V = V[~V.task.str.contains("_by_session")]
T = T.merge(V[["task", "gene", "var_donor", "var_slide", "var_spot", "frac_donor",
               "frac_slide", "n_donors", "df_donor", "donor_label_status"]],
            on=["task", "gene"], how="left")
T["notes"] = np.where(T.task == "PRAD",
                      "novel-slide term is partly per-session in the FEATURES (R4, 0.977 "
                      "separable); R6 found zero between-session EXPRESSION variance", "")
T.to_csv(f"{OUT}/pergene_decomposition.csv", index=False)
print(f"\nwrote {OUT}/pergene_decomposition.csv ({len(T)} encoder-task-gene rows)")

# ------------------------------------------------------------------ correlations
pairs = [("random_minus_patient", "frac_donor"), ("random_minus_patient", "var_donor"),
         ("blocked_minus_patient", "frac_donor"), ("novel_slide", "frac_slide"),
         ("same_patient_other_slide", "frac_donor"), ("replicate_leak", "frac_donor"),
         ("replicate_leak", "random_minus_patient"), ("novel_slide", "random_minus_patient")]
rows = []
for a, b in pairs:
    if a not in T or b not in T:
        continue
    for scope, sub in [("pooled", T)] + [(f"task={t}", g) for t, g in T.groupby("task")]:
        v = sub[[a, b]].dropna()
        if len(v) < 20:
            continue
        rho = spearmanr(v[a], v[b])
        rows.append(dict(x=a, y=b, scope=scope, n=len(v),
                         spearman=float(rho.statistic), p=float(rho.pvalue),
                         n_donors=int(sub.n_donors.dropna().iloc[0]) if sub.n_donors.notna().any() else -1,
                         df_donor=int(sub.df_donor.dropna().iloc[0]) if sub.df_donor.notna().any() else -1))
C = pd.DataFrame(rows)
C.to_csv(f"{OUT}/pergene_correlations.csv", index=False)
print(f"wrote {OUT}/pergene_correlations.csv ({len(C)} rows)")
print("\n=== pooled Spearman correlations ===")
print(C[C.scope == "pooled"][["x", "y", "n", "spearman", "p"]].round(4).to_string(index=False))
print("\n=== random-minus-patient vs frac_donor, per task (df_donor>=3 are the meaningful ones) ===")
z = C[(C.x == "random_minus_patient") & (C.y == "frac_donor") & (C.scope != "pooled")]
print(z[["scope", "n", "df_donor", "spearman", "p"]].round(4).to_string(index=False))

with open(f"{OUT}/PROVENANCE__r7.txt", "w") as f:
    f.write(
        "Round 2, stage R7 - per-gene decomposition\n"
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
        f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
        f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
        f"script          : code/scripts/round2_r7_pergene.py\n"
        f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
        "inputs          : R3 pergene__*.parquet, R5c pergene_replicate_leak__*.parquet, "
        "R6 donor_variance_components.csv\n"
        "join            : BETWEEN-DONOR variance per directive 2.4, not between-patient\n"
        "plan            : round2_R5_decisions.md directive 2.4 / plan phase-7\n")
