#!/usr/bin/env python
"""Round 2, R1b: oversight directives D3 and D4.

D3. COAD's patient-design dispersion is sd 0.0017 across two folds and three encoders,
    far tighter than any other task. Print the six underlying values. If the two folds
    agree to four decimals for each encoder, something in the fold construction or the
    scoring is being repeated.

D4. HEST's metadata carries `pixel_size_um_embedded` (read from the TIFF header) alongside
    `pixel_size_um_estimated` (from spot spacing). Add it to sample_metadata.csv and report
    the per-sample ratio. Agreement within a few percent means the resolution table rests
    on two independent sources; disagreement flags that sample's resolution group as
    uncertain before R3 and R4 stratify on it.
"""
import os
import time

import numpy as np
import pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"
HEST = f"{ROOT}/code/HEST/assets/HEST_v1_1_0.csv"
SPLITS = f"{ROOT}/results/tailored/splits/split_decomposition.csv"
OUT = f"{ROOT}/results/round2/R1b_heads"
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------- D3
sd = pd.read_csv(SPLITS)
coad = sd[(sd.task == "COAD") & (sd.design == "patient")].copy()
cols = [c for c in ["encoder", "fold", "repeat", "n_train", "n_test", "n_eval_samples",
                    "pearson_within", "pearson_pooled", "test_slide"] if c in coad.columns]
coad = coad[cols].sort_values(["encoder", "fold"])
coad.to_csv(f"{OUT}/d3_coad_patient_rows.csv", index=False)
print("=== D3: every COAD patient-design row ===")
print(coad.to_string(index=False))
print(f"\nrows: {len(coad)}   sd(pearson_within) = {coad.pearson_within.std():.6f}")

piv = coad.pivot_table(index="encoder", columns="fold", values="pearson_within", aggfunc="mean")
print("\nwithin-slide Pearson, encoder x fold:")
print(piv.to_string())
if piv.shape[1] >= 2:
    gap = (piv.iloc[:, 0] - piv.iloc[:, 1]).abs()
    print(f"\n|fold0 - fold1| per encoder: {gap.round(8).to_dict()}")
    identical = bool((gap < 1e-4).all())
    print(f"folds agree to 4 decimals for EVERY encoder: {identical}")
    if identical:
        print("  -> D3 CONCLUSION: not a coincidence. The two folds are producing the same "
              "score, so either the fold construction yields the same evaluation set or the "
              "scoring is being repeated. Needs fixing before R3 reuses this machinery.")
    else:
        print("  -> D3 CONCLUSION: folds differ; the tight sd is genuine low variance, not a "
              "repeated computation.")
    # is the evaluated slide the same in both folds?
    if "test_slide" in coad.columns:
        print(f"\ntest_slide by fold: "
              f"{coad.groupby('fold')['test_slide'].apply(lambda s: sorted(set(s.dropna()))).to_dict()}")
    print(f"n_test by fold: {coad.groupby('fold')['n_test'].apply(lambda s: sorted(set(s))).to_dict()}")
    print(f"n_train by fold: {coad.groupby('fold')['n_train'].apply(lambda s: sorted(set(s))).to_dict()}")

# ----------------------------------------------------------------------------- D4
sm = pd.read_csv(META)
h = pd.read_csv(HEST, low_memory=False)
idcol = next((c for c in ("id", "sample_id", "hest_id") if c in h.columns), None)
assert idcol, f"no id column in {HEST}: {list(h.columns)[:12]}"
assert "pixel_size_um_embedded" in h.columns, "pixel_size_um_embedded absent from HEST metadata"

emb = h.set_index(idcol)["pixel_size_um_embedded"]
sm["pixel_size_um_embedded"] = sm["sample_id"].map(emb)
n_have = int(sm.pixel_size_um_embedded.notna().sum())
print(f"\n\n=== D4: embedded vs estimated pixel size ===")
print(f"embedded value present for {n_have}/{len(sm)} benchmark samples")

sm["px_ratio_embedded_over_estimated"] = (sm.pixel_size_um_embedded
                                          / sm.pixel_size_um_estimated)
sm["px_pct_diff"] = (sm.px_ratio_embedded_over_estimated - 1.0) * 100
# A sample is flagged when the two independent sources disagree by more than 5%.
sm["resolution_uncertain"] = (sm.px_pct_diff.abs() > 5.0) | sm.pixel_size_um_embedded.isna()

d = sm.dropna(subset=["px_ratio_embedded_over_estimated"])
if len(d):
    print(f"ratio: median {d.px_ratio_embedded_over_estimated.median():.4f}  "
          f"IQR [{d.px_ratio_embedded_over_estimated.quantile(.25):.4f}, "
          f"{d.px_ratio_embedded_over_estimated.quantile(.75):.4f}]  "
          f"min {d.px_ratio_embedded_over_estimated.min():.4f}  "
          f"max {d.px_ratio_embedded_over_estimated.max():.4f}")
    print(f"|percent difference|: median {d.px_pct_diff.abs().median():.3f}%  "
          f"max {d.px_pct_diff.abs().max():.3f}%")
    print(f"samples beyond 5%: {int((d.px_pct_diff.abs() > 5).sum())}  "
          f"beyond 1%: {int((d.px_pct_diff.abs() > 1).sum())}")
    print("\nper task:")
    print(d.groupby("task").agg(n=("sample_id", "size"),
                                median_pct=("px_pct_diff", lambda s: round(s.median(), 3)),
                                max_abs_pct=("px_pct_diff", lambda s: round(s.abs().max(), 3)),
                                n_flagged=("resolution_uncertain", "sum")).to_string())
    worst = d.reindex(d.px_pct_diff.abs().sort_values(ascending=False).index).head(8)
    print("\nworst eight samples:")
    print(worst[["task", "sample_id", "pixel_size_um_estimated", "pixel_size_um_embedded",
                 "px_pct_diff", "resolution_group"]].round(4).to_string(index=False))

    # does the embedded value ever change a sample's resolution group?
    BINS = [0.0, 0.15, 0.23, 0.30, 0.40, 0.50, np.inf]
    LAB = ["<=0.15", "0.15-0.23", "0.23-0.30", "0.30-0.40", "0.40-0.50", ">0.50"]
    grp_emb = pd.cut(sm.pixel_size_um_embedded, bins=BINS, labels=LAB, right=True)
    moved = sm[(grp_emb.astype(str) != sm.resolution_group.astype(str))
               & sm.pixel_size_um_embedded.notna()]
    print(f"\nsamples whose resolution_group would CHANGE under the embedded value: {len(moved)}")
    if len(moved):
        m = moved.copy(); m["group_embedded"] = grp_emb[moved.index]
        print(m[["task", "sample_id", "pixel_size_um_estimated", "pixel_size_um_embedded",
                 "resolution_group", "group_embedded"]].round(4).to_string(index=False))

sm.to_csv(META, index=False)
sm[["task", "sample_id", "patient", "pixel_size_um", "pixel_size_um_estimated",
    "pixel_size_um_embedded", "px_ratio_embedded_over_estimated", "px_pct_diff",
    "resolution_group", "resolution_uncertain"]].to_csv(f"{OUT}/d4_pixel_size_check.csv",
                                                        index=False)
print(f"\nflagged resolution_uncertain: {int(sm.resolution_uncertain.sum())}/{len(sm)} samples")

with open(f"{OUT}/PROVENANCE__d3_d4.txt", "w") as f:
    f.write(f"Round 2, R1b - directives D3 and D4\n"
            f"slurm_job_id      : {os.environ.get('SLURM_JOB_ID','NA')}\n"
            f"slurm_partition   : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
            f"node              : {os.environ.get('SLURMD_NODENAME','NA')}\n"
            f"date              : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit       : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
            f"script            : code/scripts/round2_r1b_d3_d4.py\n"
            f"config_hash       : d3d4-v1-embedded5pct\n"
            f"config            : flag threshold 5 percent on |embedded/estimated - 1|; "
            f"D3 reads {SPLITS}; D4 reads {HEST}\n"
            f"decisions         : round2_R1_decisions.md directives D3, D4\n")
