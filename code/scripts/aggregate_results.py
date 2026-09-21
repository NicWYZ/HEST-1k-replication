#!/usr/bin/env python
"""Aggregate the faithful-run results into the official summary tables.

Stage: faithful replication, results aggregation (HEST_replication_handoff.md stage 4).

INPUT   results/faithful/<head>/<encoder>/<task>/results_kfold.json
OUTPUT  results/summary/results_split.csv    head x encoder x task x split -> per-fold Pearson
        results/summary/results_task.csv     head x encoder x task        -> mean/std over folds
        results/summary/results_gene.csv     head x encoder x task x gene -> mean Pearson
        results/summary/results_encoder.csv  head x encoder               -> average over tasks

HEADS. Named <features>_<model>, matching the four configurations the paper reports:
  pca_ridge  PCA-256 features + ridge   the Table 1 protocol
  raw_ridge  raw embeddings  + ridge    Table A13
  raw_xgb    raw embeddings  + XGBoost  Table A14, the configuration the paper used
  pca_xgb    PCA-256 features + XGBoost Table A14's rejected candidate, kept as the evidence
                                        for that selection (resnet50 only)

WHY THIS IS NOW SIMPLE. Earlier versions of this script parsed HEST's raw output directory
names (`<exp_code>::<timestamp>`) and had to cope with three hazards: ad-hoc exp_code
prefixes that varied per submission wave, `_part2` completion runs for jobs killed at their
wall limit, and partial task directories with no results_kfold.json. Two silent failures came
out of that: a missing exp_code prefix routed ten encoders to a skip branch that reported only
to stderr, and a per-directory (rather than per-task) merge once kept a 4-task completion run
while discarding the 6 tasks it was meant to complete.

code/scripts/reorganize_repo.py now resolves all three ON DISK -- one directory per
(head, encoder, task), partial tasks dropped, completion runs merged -- so this script just
walks a fixed tree. If a task is missing here, it is genuinely missing rather than hidden by
a naming mismatch, and the integrity block at the end will say so.
"""
import os, json, sys
import pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
RES  = os.path.join(ROOT, "results", "faithful")
OUT  = os.path.join(ROOT, "results", "summary")
os.makedirs(OUT, exist_ok=True)

# HCC is excluded from the paper's own averages; kept in the tables as avg_all10
PAPER_TASKS = ["IDC", "PRAD", "PAAD", "SKCM", "COAD", "READ", "CCRCC", "LUNG", "LYMPH_IDC"]
EXPECTED_TASKS = set(PAPER_TASKS) | {"HCC"}

split_rows, gene_rows, missing = [], [], []
for head in sorted(d for d in os.listdir(RES) if os.path.isdir(os.path.join(RES, d))):
    for enc in sorted(os.listdir(os.path.join(RES, head))):
        ep = os.path.join(RES, head, enc)
        if not os.path.isdir(ep):
            continue
        found = set()
        for task in sorted(os.listdir(ep)):
            kf = os.path.join(ep, task, "results_kfold.json")
            if not os.path.isfile(kf):
                continue
            found.add(task)
            with open(kf) as f:
                r = json.load(f)
            for i, v in enumerate(r.get("mean_per_split", [])):
                split_rows.append(dict(head=head, encoder=enc, task=task, split=i, pearson=v))
            for g in r.get("pearson_corrs", []):
                gene_rows.append(dict(head=head, encoder=enc, task=task, gene=g.get("name"),
                                      pearson_mean=g.get("mean")))
        gap = EXPECTED_TASKS - found
        if gap:
            missing.append((head, enc, sorted(gap)))

if not split_rows:
    sys.exit("no results found - nothing aggregated")

split_df = pd.DataFrame(split_rows)
gene_df  = pd.DataFrame(gene_rows)

task_df = (split_df.groupby(["head", "encoder", "task"], as_index=False)
           .agg(pearson_mean=("pearson", "mean"), pearson_std=("pearson", "std"),
                n_splits=("pearson", "size")))
task_df["pearson_mean"] = task_df.pearson_mean.round(4)
task_df["pearson_std"]  = task_df.pearson_std.round(4)

def enc_avg(g):
    p9 = g.loc[g["task"].isin(PAPER_TASKS), "pearson_mean"]
    return pd.Series({"avg_paper9": round(p9.mean(), 4) if len(p9) else float("nan"),
                      "n_tasks_paper9": int(len(p9)),
                      "avg_all10": round(g.pearson_mean.mean(), 4),
                      "n_tasks_all": int(len(g))})
enc_df = task_df.groupby(["head", "encoder"]).apply(enc_avg, include_groups=False).reset_index()

split_df.to_csv(os.path.join(OUT, "results_split.csv"), index=False)
task_df.to_csv(os.path.join(OUT, "results_task.csv"), index=False)
gene_df.to_csv(os.path.join(OUT, "results_gene.csv"), index=False)
enc_df.sort_values(["head", "avg_paper9"], ascending=[True, False]).to_csv(
    os.path.join(OUT, "results_encoder.csv"), index=False)

print(f"rows -> split {len(split_df)}, task {len(task_df)}, gene {len(gene_df)}, encoder {len(enc_df)}")
for head in sorted(enc_df["head"].unique()):
    sub = enc_df[enc_df["head"] == head].sort_values("avg_paper9", ascending=False)
    print(f"\n=== {head} (avg over the 9 paper tasks; HCC excluded) ===")
    print(sub[["encoder", "avg_paper9", "n_tasks_paper9", "avg_all10"]].to_string(index=False))

print("\n--- integrity ---")
print("task rows with NaN mean :", int(task_df.pearson_mean.isna().sum()))
print("tasks per (head,encoder):", sorted(task_df.groupby(["head", "encoder"]).size().unique().tolist()))
print("encoders per head       :", enc_df.groupby("head").encoder.nunique().to_dict())
if missing:
    print("INCOMPLETE (head, encoder, missing tasks):")
    for h, e, g in missing:
        print(f"  {h} / {e}: {g}")
else:
    print("every (head, encoder) covers all 10 tasks")
