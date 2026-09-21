#!/usr/bin/env python
"""Rebuild the analysis tables in results/summary/ that the aggregation script does not produce.

Stage: faithful replication, derived summary tables (HEST_replication_handoff.md stage 4); rerun after any results change.

aggregate_results.py rebuilds results_{split,task,gene,encoder}.csv straight from
results/faithful. The three tables below are ANALYSIS products layered on top of those, and
were previously hand-maintained -- which is how they came to carry stale head names
(`ridge_nopca`, `xgb_nopca`) after the heads were renamed, and to miss hoptimus1 after it ran.
This script derives them so that can no longer drift.

  discrepancy_table.csv              head x encoder x task, with the leaderboard value and diff
  head_comparison_paper9.csv         encoder x head, with embedding dimension
  faithful_pca_ridge_task_matrix.csv encoder x task matrix for the Table 1 protocol

NOT rebuilt here: scaling_law_inputs.csv. That table compares against the PAPER's Table 1
(columns paper_avg / paper_printed / paper_rank), and the paper reports 10 encoders. conch_v15
and hoptimus1 postdate it -- hoptimus1 appears on the live leaderboard but not in the paper --
so adding rows would require paper values that do not exist. It correctly stays at 10.

LEADERBOARD SEMANTICS. `leaderboard` is populated wherever the snapshot has a value for that
(encoder, task), including for heads other than pca_ridge, but `compare_to_leaderboard` is True
ONLY for pca_ridge. The leaderboard reports the Table 1 protocol, so a raw_ridge or raw_xgb row
is a different configuration and its diff is not a replication discrepancy. HCC is absent from
the leaderboard entirely, so its diff is null by construction, not by omission.
"""
import os
import pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
S = os.path.join(ROOT, "results", "summary")

PAPER_TASKS = ["IDC", "PRAD", "PAAD", "SKCM", "COAD", "READ", "CCRCC", "LUNG", "LYMPH_IDC"]
DIM = {"resnet50": 1024, "ctranspath": 768, "phikon": 768, "conch_v1": 512, "conch_v15": 768,
       "uni_v1": 1024, "uni_v2": 1536, "gigapath": 1536, "virchow": 2560, "virchow2": 2560,
       "hoptimus0": 1536, "hoptimus1": 1536}
ROLE = {"pca_ridge": "replicates Table 1 / leaderboard",
        "raw_ridge": "replicates Table A13",
        "raw_xgb":   "A14 candidate - selected",
        "pca_xgb":   "A14 candidate - rejected"}

task = pd.read_csv(os.path.join(S, "results_task.csv"))
lb = pd.read_csv(os.path.join(S, "hest_leaderboard_030426.csv"))
lb = lb[lb.encoder.notna()].copy()

# long-form leaderboard: encoder x task -> value
lb_long = lb.melt(id_vars=["encoder"], value_vars=[t for t in PAPER_TASKS if t in lb.columns],
                  var_name="task", value_name="leaderboard")

d = task.merge(lb_long, on=["encoder", "task"], how="left")
d["diff_vs_leaderboard"] = (d.pearson_mean - d.leaderboard).round(4)
d["config_role"] = d["head"].map(ROLE)
d["compare_to_leaderboard"] = d["head"].eq("pca_ridge")
assert d.config_role.notna().all(), "a head has no config_role"
d = d.sort_values(["head", "encoder", "task"])
d.to_csv(os.path.join(S, "discrepancy_table.csv"), index=False)

# head comparison, one row per encoder
enc = pd.read_csv(os.path.join(S, "results_encoder.csv"))
hc = enc.pivot(index="encoder", columns="head", values="avg_paper9")
hc.insert(0, "dim", [DIM[e] for e in hc.index])
if {"raw_xgb", "raw_ridge"} <= set(hc.columns):
    hc["xgb_minus_ridge"] = (hc.raw_xgb - hc.pca_ridge).round(4)
hc = hc.sort_values("pca_ridge", ascending=False).round(4)
hc.reset_index().to_csv(os.path.join(S, "head_comparison_paper9.csv"), index=False)

# encoder x task matrix for the primary head
m = (task[task["head"] == "pca_ridge"]
     .pivot(index="encoder", columns="task", values="pearson_mean")
     .reindex(columns=PAPER_TASKS + ["HCC"]))
m = m.loc[hc.index.intersection(m.index)]
m.reset_index().to_csv(os.path.join(S, "faithful_pca_ridge_task_matrix.csv"), index=False)

print("=== discrepancy_table.csv ===")
print(f"  rows {len(d)} | heads {sorted(d['head'].unique())}")
print(f"  encoders {d.encoder.nunique()} | hoptimus1 rows {int((d.encoder=='hoptimus1').sum())}")
lbp = d[d.compare_to_leaderboard & d.leaderboard.notna()]
ad = lbp.diff_vs_leaderboard.abs()
print(f"  leaderboard-comparable cells: {len(lbp)} ({lbp.encoder.nunique()} encoders x 9 tasks)")
print(f"  mean |diff| {ad.mean():.5f} | median {ad.median():.5f} | max {ad.max():.4f} "
      f"({lbp.loc[ad.idxmax(),'encoder']}/{lbp.loc[ad.idxmax(),'task']})")
print(f"  over 0.03: {int((ad>0.03).sum())} of {len(lbp)}")
print(f"  HCC rows with a leaderboard value: {int(d[d.task=='HCC'].leaderboard.notna().sum())} (expect 0)")
print("\n=== head_comparison_paper9.csv ===")
print(hc.to_string())
print("\n=== faithful_pca_ridge_task_matrix.csv ===")
print(f"  {m.shape[0]} encoders x {m.shape[1]} tasks | NaN cells {int(m.isna().sum().sum())}")
print("\n=== stale-name check ===")
stale = [c for c in ("ridge_nopca", "xgb_nopca") if c in set(d["head"]) | set(hc.columns)]
print("  legacy head names remaining:", stale if stale else "none")
