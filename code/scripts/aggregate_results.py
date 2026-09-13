#!/usr/bin/env python
"""Aggregate all faithful-run results into tidy tables for Stage 3.

Reads results/faithful/<exp_code>::<ts>/<task>/<encoder>/results_kfold.json and emits:
  reports/results_task.csv     head x encoder x task -> mean/std over folds
  reports/results_split.csv    head x encoder x task x split -> per-fold Pearson
  reports/results_gene.csv     head x encoder x task x gene -> mean Pearson
  reports/results_encoder.csv  head x encoder -> average over tasks (paper-9 and all-10)

The smoke run is excluded: it duplicates faithful_pca_ridge__resnet50.
Where an exp_code was run more than once, the LATEST timestamp wins (and is reported).
"""
import os, json, glob, re, sys
import pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
RES  = os.path.join(ROOT, "results", "faithful")
OUT  = os.path.join(ROOT, "reports")
os.makedirs(OUT, exist_ok=True)

PAPER_TASKS = ["IDC","PRAD","PAAD","SKCM","COAD","READ","CCRCC","LUNG","LYMPH_IDC"]  # HCC excluded
HEAD_MAP = {"faithful_pca_ridge": "pca_ridge", "faithful_ridge": "ridge_nopca", "faithful_xgb": "xgb_pca"}

# ---- resolve exp dirs, keeping only the newest timestamp per exp_code ----
newest = {}
for d in sorted(glob.glob(os.path.join(RES, "*::*"))):
    base = os.path.basename(d)
    exp, ts = base.split("::", 1)
    if exp.startswith("smoke_"):
        continue
    m = re.match(r"^(faithful_pca_ridge|faithful_ridge|faithful_xgb)__(.+)$", exp)
    if not m:
        print(f"[skip] unrecognised exp_code: {exp}", file=sys.stderr); continue
    head, enc = HEAD_MAP[m.group(1)], m.group(2)
    key = (head, enc)
    if key not in newest or ts > newest[key][0]:
        newest[key] = (ts, d)

split_rows, gene_rows = [], []
for (head, enc), (ts, d) in sorted(newest.items()):
    for kf in sorted(glob.glob(os.path.join(d, "*", "*", "results_kfold.json"))):
        task = os.path.basename(os.path.dirname(os.path.dirname(kf)))
        with open(kf) as f:
            r = json.load(f)
        for i, v in enumerate(r.get("mean_per_split", [])):
            split_rows.append(dict(head=head, encoder=enc, task=task, split=i,
                                   pearson=v, run_ts=ts))
        for g in r.get("pearson_corrs", []):
            gene_rows.append(dict(head=head, encoder=enc, task=task,
                                  gene=g.get("name"), pearson_mean=g.get("mean"),
                                  n_splits=len(g.get("pearson_corrs", []))))

if not split_rows:
    sys.exit("no results found - nothing aggregated")

split_df = pd.DataFrame(split_rows)
gene_df  = pd.DataFrame(gene_rows)

# task-level: mean/std over folds. Matches the benchmark's own dataset_results.csv.
task_df = (split_df.groupby(["head","encoder","task"], as_index=False)
           .agg(pearson_mean=("pearson","mean"), pearson_std=("pearson","std"),
                n_splits=("pearson","size"), run_ts=("run_ts","first")))
task_df["pearson_mean"] = task_df.pearson_mean.round(4)
task_df["pearson_std"]  = task_df.pearson_std.round(4)

# encoder-level: unweighted mean over tasks, the paper's convention
def enc_avg(g):
    p9 = g.loc[g["task"].isin(PAPER_TASKS), "pearson_mean"]
    return pd.Series({  # noqa: E501

        "avg_paper9": round(p9.mean(), 4) if len(p9) else float("nan"),
        "n_tasks_paper9": int(len(p9)),
        "avg_all10": round(g.pearson_mean.mean(), 4),
        "n_tasks_all": int(len(g)),
    })
enc_df = task_df.groupby(["head","encoder"]).apply(enc_avg, include_groups=False).reset_index()

split_df.to_csv(os.path.join(OUT, "results_split.csv"), index=False)
task_df.to_csv(os.path.join(OUT, "results_task.csv"), index=False)
gene_df.to_csv(os.path.join(OUT, "results_gene.csv"), index=False)
enc_df.sort_values(["head","avg_paper9"], ascending=[True, False]).to_csv(
    os.path.join(OUT, "results_encoder.csv"), index=False)

print(f"exp dirs used: {len(newest)}")
print(f"rows -> split {len(split_df)}, task {len(task_df)}, gene {len(gene_df)}, encoder {len(enc_df)}")
print()
for head in sorted(enc_df["head"].unique()):
    sub = enc_df[enc_df["head"] == head].sort_values("avg_paper9", ascending=False)
    print(f"=== {head} (avg over the 9 paper tasks; HCC excluded) ===")
    print(sub[["encoder","avg_paper9","n_tasks_paper9","avg_all10"]].to_string(index=False))
    print()
# integrity checks
bad = task_df[task_df.pearson_mean.isna()]
print("task rows with NaN mean:", len(bad))
print("tasks per (head,encoder):", sorted(task_df.groupby(['head','encoder']).size().unique().tolist()))
