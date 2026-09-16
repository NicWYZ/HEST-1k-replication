#!/usr/bin/env python
"""Aggregate all faithful-run results into tidy tables for Stage 3.

Reads results/faithful/<exp_code>::<ts>/<task>/<encoder>/results_kfold.json and emits:
  reports/results_task.csv     head x encoder x task -> mean/std over folds
  reports/results_split.csv    head x encoder x task x split -> per-fold Pearson
  reports/results_gene.csv     head x encoder x task x gene -> mean Pearson
  reports/results_encoder.csv  head x encoder -> average over tasks (paper-9 and all-10)

The smoke run is excluded: it duplicates faithful_pca_ridge__resnet50.

MERGING ACROSS RUNS. A wide-embedding run that hit its wall was finished by a second job whose
exp_code carries a `_part2` suffix and covers only the tasks the first run never reached. Those
land in a SEPARATE `<exp>::<ts>` directory. Resolution is therefore per (head, encoder, TASK),
not per (head, encoder): every matching directory is scanned and, for a task present in more
than one, the newest timestamp wins. Taking `sorted(dirs)[-1]` per exp_code -- the previous
behaviour -- would have silently kept only the 4-task completion run and discarded the 6 tasks
from the original, yielding a plausible but wrong encoder average.
"""
import os, json, glob, re, sys
import pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
RES  = os.path.join(ROOT, "results", "faithful")
TAILORED = os.path.join(ROOT, "results", "tailored")   # probe_* experiments live here
OUT  = os.path.join(ROOT, "reports")
os.makedirs(OUT, exist_ok=True)

PAPER_TASKS = ["IDC","PRAD","PAAD","SKCM","COAD","READ","CCRCC","LUNG","LYMPH_IDC"]  # HCC excluded
# `a14_xgb_raw` is the exp_code the ten-encoder Table A14 fan-out used, after the resnet50 pilot
# (`probe_xgb_nopca`) established that the paper fed RAW embeddings to XGBoost. Both prefixes map to
# the same head so the pilot and the fan-out MERGE rather than one shadowing the other. Omitting it
# silently routed all ten encoders to the [skip] branch below, which reports to stderr -- so the
# table showed xgb_nopca with 1 encoder instead of 11 and looked plausible.
HEAD_MAP = {"faithful_pca_ridge": "pca_ridge", "faithful_ridge": "ridge_nopca",
            "faithful_xgb": "xgb_pca", "probe_xgb_nopca": "xgb_nopca",
            "a14_xgb_raw": "xgb_nopca"}
# a `_part2` suffix marks a completion run for the same head; it is stripped before mapping
# Alternation derived from HEAD_MAP rather than written out, so adding a head cannot leave the
# regex behind. Longest-first ordering matters: bare alternation would let a shorter prefix win.
_ALT = "|".join(sorted(HEAD_MAP, key=len, reverse=True))
EXP_RE = re.compile(r"^(" + _ALT + r")(?:_part\d+)?__(.+)$")
# ---- resolve results per (head, encoder, TASK); newest timestamp wins ----
# Keyed on task as well as encoder so a `_part2` completion run MERGES with the original
# instead of replacing it. An empty directory (a run that died before writing anything)
# contributes nothing and cannot shadow a good one, because only files found are recorded.
chosen = {}
scanned = 0
for base_dir in (RES, TAILORED):
    for d in sorted(glob.glob(os.path.join(base_dir, "*::*"))):
        exp, ts = os.path.basename(d).split("::", 1)
        if exp.startswith("smoke_"):
            continue
        m = EXP_RE.match(exp)
        if not m:
            print(f"[skip] unrecognised exp_code: {exp}", file=sys.stderr); continue
        head, enc = HEAD_MAP[m.group(1)], m.group(2)
        scanned += 1
        for kf in sorted(glob.glob(os.path.join(d, "*", "*", "results_kfold.json"))):
            task = os.path.basename(os.path.dirname(os.path.dirname(kf)))
            key = (head, enc, task)
            if key not in chosen or ts > chosen[key][0]:
                chosen[key] = (ts, kf)

split_rows, gene_rows = [], []
for (head, enc, task), (ts, kf) in sorted(chosen.items()):
    if True:
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

print(f"exp dirs scanned: {scanned}; (head,encoder,task) results resolved: {len(chosen)}")
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
