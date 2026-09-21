#!/usr/bin/env python
"""Build results/summary/deck_numbers.csv -- one row per number the deck asserts.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.3).
Output: results/summary/deck_numbers.csv
        columns slide, label, value, source_file, source_column_or_query

Every value is READ from its source file here, never typed. The point of the
file is that `verify_numeric_claims.py` can then check the outline against a
single table instead of against thirty scattered CSVs, and that any number in
the deck which no repository file supports becomes visible as a missing row
rather than as prose nobody checked.

Scope. Slide 7 is a literature slide: its figures (0.42, 0.415, ~100%) come from
published papers, not from this repository, so they are deliberately absent and
reported as out of scope rather than invented. Two numbers on slide 9 describe
the target distribution (the log1p mean of about 0.6) and are recomputed here
from the per-gene head metrics.

Where a bullet states a range over tasks or encoders ("0.050 to 0.193", "0.87 to
0.95"), both endpoints get their own row, because a range whose ends are not
separately checkable is not checkable at all.
"""
import glob
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
OUT = f"{ROOT}/results/summary/deck_numbers.csv"

rows = []
missing = []


def read(rel):
    p = f"{ROOT}/{rel}"
    if not os.path.exists(p):
        missing.append(rel)
        return None
    return pd.read_csv(p)


def add(slide, label, value, src, query):
    """One checkable number. `value` None means the source was absent."""
    if value is None:
        return
    rows.append(dict(slide=slide, label=label, value=float(value),
                     source_file=src, source_column_or_query=query))


# ------------------------------------------------------------------ slide 3
DT = read("results/summary/discrepancy_table.csv")
if DT is not None:
    # 120 rows carry the compare flag but 12 of them have no leaderboard value
    # (HCC is not on the leaderboard), so the comparison is over 108 cells --
    # 12 encoders x 9 tasks. Counting the flag alone gives 120 and is wrong.
    cmp_ = DT[DT.compare_to_leaderboard.astype(str).str.lower().isin(["true", "1"])]
    cmp_ = cmp_[cmp_.diff_vs_leaderboard.notna()]
    ad = cmp_.diff_vs_leaderboard.abs()
    add(3, "encoder-task cells compared with the live leaderboard", len(cmp_),
        "results/summary/discrepancy_table.csv",
        "rows with compare_to_leaderboard true and a non-null diff_vs_leaderboard")
    add(3, "mean absolute difference from the leaderboard", ad.mean(),
        "results/summary/discrepancy_table.csv", "mean |diff_vs_leaderboard|")
    add(3, "largest absolute difference from the leaderboard", ad.max(),
        "results/summary/discrepancy_table.csv", "max |diff_vs_leaderboard|")
    add(3, "cells exceeding the 0.03 acceptance threshold", int((ad > 0.03).sum()),
        "results/summary/discrepancy_table.csv", "count |diff_vs_leaderboard| > 0.03")
    # The appendix-table discrepancy round 1 recorded as D1 is an ENCODER-LEVEL
    # average over the nine paper tasks, not a per-task cell: ResNet50's raw-ridge
    # average sits about 0.03 below the published Table A13 value. Per task the
    # raw-ridge differences are far larger and of one sign for the wide encoders,
    # which is the numerical-conditioning story of slide 6 rather than a
    # reproduction failure, so both levels get a row.
    a13 = DT[(DT.config_role == "replicates Table A13") & DT.diff_vs_leaderboard.notna()]
    r50 = a13[a13.encoder == "resnet50"]
    if len(r50):
        add(3, "ResNet50 raw-ridge average minus the published Table A13 value",
            r50.diff_vs_leaderboard.mean(),
            "results/summary/discrepancy_table.csv",
            "mean diff_vs_leaderboard where head=raw_ridge, encoder=resnet50, "
            "config_role=replicates Table A13")
    add(6, "mean absolute per-task difference from the published Table A13",
        a13.diff_vs_leaderboard.abs().mean(),
        "results/summary/discrepancy_table.csv",
        "mean |diff_vs_leaderboard| where config_role=replicates Table A13")
    add(6, "largest per-task difference from the published Table A13",
        a13.diff_vs_leaderboard.abs().max(),
        "results/summary/discrepancy_table.csv",
        "max |diff_vs_leaderboard| where config_role=replicates Table A13")

RE = read("results/summary/results_encoder.csv")
if RE is not None:
    pca = RE[RE["head"] == "pca_ridge"].set_index("encoder")
    for enc, nm in (("resnet50", "ResNet50"), ("hoptimus1", "H-Optimus-1")):
        add(3, f"{nm} average over the nine paper tasks", pca.loc[enc, "avg_paper9"],
            "results/summary/results_encoder.csv", f"avg_paper9 where encoder={enc}")
    add(5, "between-encoder spread on the benchmark protocol",
        pca.avg_paper9.max() - pca.avg_paper9.min(),
        "results/summary/results_encoder.csv", "max(avg_paper9) - min(avg_paper9)")
    add(5, "best encoder average (H-Optimus-1)", pca.avg_paper9.max(),
        "results/summary/results_encoder.csv", "max(avg_paper9)")
    add(5, "worst encoder average (ResNet50)", pca.avg_paper9.min(),
        "results/summary/results_encoder.csv", "min(avg_paper9)")

# ------------------------------------------------------------- slides 4 and 5
PT = read("results/round2/R3_splits/r3_per_task_terms.csv")
if PT is not None:
    g = PT.set_index("task")["TOTAL random - patient"]
    add(4, "COAD random-minus-patient gap", g.loc["COAD"],
        "results/round2/R3_splits/r3_per_task_terms.csv", "TOTAL random - patient, COAD")
    others = g.drop("COAD")
    add(4, "smallest random-minus-patient gap among the other nine tasks", others.min(),
        "results/round2/R3_splits/r3_per_task_terms.csv", "min over tasks except COAD")
    add(4, "largest random-minus-patient gap among the other nine tasks", others.max(),
        "results/round2/R3_splits/r3_per_task_terms.csv", "max over tasks except COAD")
    add(4, "IDC random-minus-patient gap", g.loc["IDC"],
        "results/round2/R3_splits/r3_per_task_terms.csv", "TOTAL random - patient, IDC")
    add(11, "novel-slide term, multi-slide tasks", PT["novel slide"].mean(),
        "results/round2/R3_splits/r3_per_task_terms.csv", "mean of novel slide")
    add(11, "novel-patient term, multi-slide tasks", PT["same patient, other slide"].mean(),
        "results/round2/R3_splits/r3_per_task_terms.csv", "mean of same patient, other slide")
    add(5, "COAD novel-slide term standard deviation from zero",
        PT.set_index("task").loc["COAD", "novel slide"],
        "results/round2/R3_splits/r3_per_task_terms.csv", "novel slide, COAD")

DEC = read("results/round2/R3_splits/r3_decomposition_terms.csv")
if DEC is not None:
    D = DEC.set_index("term")["mean"]
    NAMES = {"training-set size": "training-set size term",
             "spatial adjacency, size matched": "spatial adjacency term",
             "residual adjacency (buffer)": "residual adjacency term removed only by a buffer",
             "patient identity": "slide-and-patient identity term",
             "novel slide": "novel-slide term",
             "same patient, other slide": "novel-patient term",
             "TOTAL random - patient": "total random-minus-patient gap"}
    for term, label in NAMES.items():
        if term in D.index:
            add(5, label, D.loc[term],
                "results/round2/R3_splits/r3_decomposition_terms.csv", f"mean where term={term}")
    # The buffered-to-patient step is not stored as its own row: the file holds the
    # three earlier steps and the total, and this step is the remainder. Recorded
    # as a derived value with the arithmetic spelled out rather than typed.
    steps3 = ["training-set size", "spatial adjacency, size matched",
              "residual adjacency (buffer)"]
    if all(t in D.index for t in steps3) and "TOTAL random - patient" in D.index:
        add(5, "slide-and-patient identity term",
            D.loc["TOTAL random - patient"] - D.loc[steps3].sum(),
            "results/round2/R3_splits/r3_decomposition_terms.csv",
            "mean(TOTAL random - patient) minus the sum of the three earlier steps")

LK = read("results/round2/R5c_leak/r5c_leak_summary.csv")
if LK is not None:
    L = LK.set_index(LK.columns[0]) if "task" not in LK.columns else LK.set_index("task")
    for t in ("IDC", "READ"):
        if t in L.index:
            add(4, f"{t} replicate leak, mean over encoder-slide cells", L.loc[t, "mean"],
                "results/round2/R5c_leak/r5c_leak_summary.csv", f"mean where task={t}")
            add(4, f"{t} encoder-slide cells measured", L.loc[t, "count"],
                "results/round2/R5c_leak/r5c_leak_summary.csv", f"count where task={t}")
            add(4, f"{t} cells with a positive leak", L.loc[t, "n_positive"],
                "results/round2/R5c_leak/r5c_leak_summary.csv", f"n_positive where task={t}")
    if "share_of_gap" in L.columns and "IDC" in L.index:
        add(4, "IDC leak as a share of its random-minus-patient gap",
            L.loc["IDC", "share_of_gap"],
            "results/round2/R5c_leak/r5c_leak_summary.csv", "share_of_gap where task=IDC")

BD = [f for f in glob.glob(f"{ROOT}/results/round2/R3_splits/buffer_diagnostics__*.csv")]
SV = [f for f in glob.glob(f"{ROOT}/results/round2/R3_splits/split_v4__*.csv")]
if SV:
    S = pd.concat([pd.read_csv(f) for f in SV], ignore_index=True)
    gr = (S[S.design.isin(["blocked", "blocked_buffered"])]
          .groupby(["design", "grid"]).pearson_within.mean().unstack("design"))
    for design, label in (("blocked", "unbuffered"), ("blocked_buffered", "buffered")):
        add(5, f"grid-size spread of the {label} blocked split",
            gr[design].max() - gr[design].min(),
            "results/round2/R3_splits/split_v4__*.csv",
            f"max-min of mean pearson_within over grid, design={design}")

# ------------------------------------------------------------------ slide 6
AS_ = read("results/tailored/regularization/alpha_sweep.csv")
if AS_ is not None:
    # is_formula_value is False on every row -- the sweep grid does not contain the
    # formula value exactly -- so the penalty comes from the formula_alpha column,
    # which the sweep records per feature width.
    fa = AS_[AS_.d == 256].formula_alpha
    if len(fa):
        add(6, "the benchmark's ridge penalty at d=256", fa.iloc[0],
            "results/tailored/regularization/alpha_sweep.csv",
            "formula_alpha where d=256")
    raw = AS_[AS_.scale == "raw"]
    if len(raw):
        add(6, "Gram condition number on raw embeddings, median", raw.gram_cond.median(),
            "results/tailored/regularization/alpha_sweep.csv",
            "median gram_cond where scale=raw")
        add(6, "Gram condition number on raw embeddings, largest", raw.gram_cond.max(),
            "results/tailored/regularization/alpha_sweep.csv",
            "max gram_cond where scale=raw")
    pca_ = AS_[AS_.scale == "pca256"]
    if len(pca_):
        add(6, "Gram condition number after PCA to 256 dimensions, median",
            pca_.gram_cond.median(),
            "results/tailored/regularization/alpha_sweep.csv",
            "median gram_cond where scale=pca256")

WC = read("results/round2/R8_raw_heads/r8_width_correlations.csv")
if WC is not None:
    # The file carries two cohorts. The 12-encoder one is round 2's, after R8 gave
    # H-Optimus-1 its raw-head cells; the 11-encoder one is round 1's. Both are
    # recorded, because the two documents quote different values for the same
    # correlation and naming the cohort is what makes either checkable.
    for n in sorted(WC.n_encoders.unique()):
        W = WC[WC.n_encoders == n]
        for key, label in (("raw_ridge mean Pearson", "raw ridge"),
                           ("pca_ridge mean Pearson", "PCA ridge")):
            m = W[W.relation.str.contains(key, regex=False)]
            if len(m):
                add(6, f"Spearman(embedding width, score) on the {label} head, "
                       f"{int(n)}-encoder cohort", m.spearman.iloc[0],
                    "results/round2/R8_raw_heads/r8_width_correlations.csv",
                    f"spearman where relation contains '{key}' and n_encoders={int(n)}")

LB = read("results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv")
if LB is not None:
    B = LB.dropna(subset=["rank_raw", "rank_pca"]).set_index("encoder")
    for enc, nm in (("hoptimus1", "H-Optimus-1"),):
        add(6, f"{nm} rank on the PCA-256 head", B.loc[enc, "rank_pca"],
            "results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv",
            f"rank_pca where encoder={enc}")
        add(6, f"{nm} rank on the raw-embedding head", B.loc[enc, "rank_raw"],
            "results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv",
            f"rank_raw where encoder={enc}")
    wide_r = B[B.width >= 1536].rank_raw
    narrow_r = B[B.width <= 1024].rank_raw
    add(6, "best raw-head rank among encoders of 1536 dimensions or more", wide_r.min(),
        "results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv",
        "min rank_raw where width>=1536")
    add(6, "worst raw-head rank among encoders of 1024 dimensions or fewer", narrow_r.max(),
        "results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv",
        "max rank_raw where width<=1024")
    add(6, "embedding width of the raw-head winner (CONCH v1)",
        B.width[B.rank_raw == B.rank_raw.min()].iloc[0],
        "results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv",
        "width where rank_raw is 1")

# ------------------------------------------------------------------ slide 9
LP = read("results/round2/R1b_heads/r1b_ladder_pooled.csv")
if LP is not None:
    p = LP.iloc[0]
    for col, label in (("faithful", "pooled fold-median R2, head as shipped"),
                       ("train-mean intercept", "pooled fold-median R2 with a training-mean intercept"),
                       ("oracle level", "pooled fold-median R2 with the test fold's own mean"),
                       ("oracle level and optimal scale",
                        "pooled fold-median R2 with an oracle level and optimal scale")):
        add(9, label, p[col], "results/round2/R1b_heads/r1b_ladder_pooled.csv", col)
    add(9, "prediction-to-target scale ratio, pooled", p["rho_over_r"],
        "results/round2/R1b_heads/r1b_ladder_pooled.csv", "rho_over_r")

LE = read("results/round2/R1b_heads/r1b_ladder_by_encoder.csv")
if LE is not None:
    E = LE.set_index("encoder")
    add(9, "largest scale ratio (ResNet50)", E.rho_over_r.max(),
        "results/round2/R1b_heads/r1b_ladder_by_encoder.csv", "max rho_over_r")
    add(9, "smallest scale ratio (UNI2-h)", E.rho_over_r.min(),
        "results/round2/R1b_heads/r1b_ladder_by_encoder.csv", "min rho_over_r")

HI = sorted(glob.glob(f"{ROOT}/results/round2/R1b_heads/head_intercept__*__f64.csv"))
if HI:
    H = pd.concat([pd.read_csv(f, usecols=["encoder", "task", "fold", "gene", "head",
                                           "r2", "train_mean_target"]) for f in HI],
                  ignore_index=True)
    sh = H[H["head"] == "nointercept_f64"]
    per_fold = sh.groupby(["task", "fold"]).r2.median()
    add(9, "folds with a negative fold-median R2 as shipped", int((per_fold < 0).sum()),
        "results/round2/R1b_heads/head_intercept__*__f64.csv",
        "count of (task,fold) with median r2 < 0 over all encoders, head nointercept_f64")
    add(9, "folds in total", int(len(per_fold)),
        "results/round2/R1b_heads/head_intercept__*__f64.csv", "distinct (task,fold)")
    add(9, "least negative fold-median R2 as shipped", per_fold.max(),
        "results/round2/R1b_heads/head_intercept__*__f64.csv", "max of the per-fold median r2")
    # Mean and median of the target differ materially (0.94 against 0.61) because the
    # per-gene means are right-skewed, so which one a bullet quotes has to be said.
    add(9, "median of the log1p target over all cells", sh.train_mean_target.median(),
        "results/round2/R1b_heads/head_intercept__*__f64.csv", "median train_mean_target")
    add(9, "mean of the log1p target over all cells", sh.train_mean_target.mean(),
        "results/round2/R1b_heads/head_intercept__*__f64.csv", "mean train_mean_target")

SSN = read("results/round2/R1b_heads/r1b_solver_sensitivity.csv")
if SSN is not None:
    encs = [c for c in SSN.columns if c not in
            ("task", "worst_encoder_mean", "max_single_gene", "verdict")]
    add("A1", "typical per-gene solver noise, median over encoder-task cells",
        float(np.nanmedian(SSN[encs].to_numpy())),
        "results/round2/R1b_heads/r1b_solver_sensitivity.csv", "median over encoder columns")
    add("A1", "largest per-gene solver noise", float(SSN.max_single_gene.max()),
        "results/round2/R1b_heads/r1b_solver_sensitivity.csv", "max of max_single_gene")

# ----------------------------------------------------------------- slide 10
P4 = read("results/round2/R4_probes/r4_probes_v2.csv")
if P4 is not None:
    p1 = P4[P4.probe == "probe1_slide_within_patient"]
    add(10, "slide identity probe, lowest of three encoders", p1.acc_blocked.min(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "min acc_blocked where probe=probe1_slide_within_patient")
    add(10, "slide identity probe, highest of three encoders", p1.acc_blocked.max(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "max acc_blocked where probe=probe1_slide_within_patient")
    add(10, "slide identity probe chance level", p1.chance.iloc[0],
        "results/round2/R4_probes/r4_probes_v2.csv", "chance, probe1")
    add(10, "classes in the slide-identity probe", p1.n_classes.iloc[0],
        "results/round2/R4_probes/r4_probes_v2.csv", "n_classes, probe1")
    add(10, "share of slide-probe errors landing in the same session",
        p1.confusion_within_subcluster_frac.mean(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "mean confusion_within_subcluster_frac, probe1")
    p1b = P4[P4.probe == "probe1b_scan_subcluster"]
    add(10, "session probe, lowest of three encoders", p1b.acc_blocked.min(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "min acc_blocked where probe=probe1b_scan_subcluster")
    add(10, "session probe, highest of three encoders", p1b.acc_blocked.max(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "max acc_blocked where probe=probe1b_scan_subcluster")
    p2 = P4[P4.probe == "probe2_2class"]
    add(10, "resolution probe, lowest of three encoders", p2.acc_pooled_balanced.min(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "min acc_pooled_balanced where probe=probe2_2class")
    add(10, "resolution probe, highest of three encoders", p2.acc_pooled_balanced.max(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "max acc_pooled_balanced where probe=probe2_2class")
    add(10, "resolution probe majority-class baseline", p2.majority_class_baseline.iloc[0],
        "results/round2/R4_probes/r4_probes_v2.csv", "majority_class_baseline, probe2")
    p3 = P4[P4.probe == "probe3_composition_adjusted"]
    m3 = p3.groupby("task").acc_drop.mean()
    add(10, "morphology adjustment removes, within PRAD patient 2", m3.loc["PRAD"],
        "results/round2/R4_probes/r4_probes_v2.csv",
        "mean acc_drop where probe=probe3 and task=PRAD")
    cross = m3.drop("PRAD")
    add(10, "morphology adjustment removes, smallest cross-patient task", cross.min(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "min mean acc_drop over cross-patient tasks")
    add(10, "morphology adjustment removes, largest cross-patient task", cross.max(),
        "results/round2/R4_probes/r4_probes_v2.csv",
        "max mean acc_drop over cross-patient tasks")

PV = read("results/round2/R6_variance/r6_prad_session_variance.csv")
if PV is not None:
    add(10, "genes whose between-session variance is at or below zero",
        int((PV.between_session_raw <= 0).sum()),
        "results/round2/R6_variance/r6_prad_session_variance.csv",
        "count between_session_raw <= 0")
    add(10, "target genes in the decomposition", len(PV),
        "results/round2/R6_variance/r6_prad_session_variance.csv", "row count")

RB = read("results/round2/R0_resolution/resolution_by_task.csv")
if RB is not None:
    add(10, "smallest pixel size across the 72 samples", RB.px_min.min(),
        "results/round2/R0_resolution/resolution_by_task.csv", "min px_min")
    add(10, "largest pixel size across the 72 samples", RB.px_max.max(),
        "results/round2/R0_resolution/resolution_by_task.csv", "max px_max")
    add(10, "pixel-size spread across the 72 samples", RB.px_max.max() / RB.px_min.min(),
        "results/round2/R0_resolution/resolution_by_task.csv", "max px_max / min px_min")
    pr = RB.set_index("task")
    add(10, "PRAD within-task pixel-size spread", pr.loc["PRAD", "spread"],
        "results/round2/R0_resolution/resolution_by_task.csv", "spread where task=PRAD")

SM = read("results/tailored/integrity/sample_metadata.csv")
if SM is not None:
    pcol = "pixel_size_um" if "pixel_size_um" in SM.columns else "pixel_size_um_estimated"
    pr = SM[SM.task == "PRAD"]
    for pat, label in (("patient 2", "PRAD patient 2"), ("patient 1", "PRAD patient 1")):
        g = pr[pr.patient == pat]
        if not len(g):
            continue
        v = np.sort(g[pcol].to_numpy())
        add(10, f"slides in {label}", len(v),
            "results/tailored/integrity/sample_metadata.csv",
            f"row count where task=PRAD and patient={pat}")
        add(10, f"{label} smallest pixel size", v.min(),
            "results/tailored/integrity/sample_metadata.csv", f"min {pcol}, {pat}")
        add(10, f"{label} largest pixel size", v.max(),
            "results/tailored/integrity/sample_metadata.csv", f"max {pcol}, {pat}")
        add(10, f"{label} within-patient pixel-size spread", v.max() / v.min(),
            "results/tailored/integrity/sample_metadata.csv", f"max/min {pcol}, {pat}")
        if len(v) > 5:
            d_ = np.diff(v)
            k = int(np.argmax(d_))
            add(10, f"{label} largest gap between consecutive pixel sizes", d_[k],
                "results/tailored/integrity/sample_metadata.csv",
                f"max of diff(sorted {pcol}), {pat}")
            add(10, f"{label} slides in the lower cluster", k + 1,
                "results/tailored/integrity/sample_metadata.csv",
                f"count below the largest gap in sorted {pcol}, {pat}")
            add(10, f"{label} slides in the upper cluster", len(v) - k - 1,
                "results/tailored/integrity/sample_metadata.csv",
                f"count above the largest gap in sorted {pcol}, {pat}")
            # The resolution probe drops the lone outlier slide, so the spread the
            # probe actually faces is over the remaining ones.
            if pat == "patient 1":
                add(10, "PRAD patient 1 pixel-size spread excluding the lone outlier",
                    v[-1] / v[1],
                    "results/tailored/integrity/sample_metadata.csv",
                    f"max/second-smallest {pcol}, patient 1")

SBP = read("results/tailored/site_probes/spatial_block_probe.csv")
if SBP is not None:
    add("A2", "slide identity under spatial-block cross-validation, all tasks",
        SBP.acc_block.mean(),
        "results/tailored/site_probes/spatial_block_probe.csv", "mean acc_block")

# ----------------------------------------------------------------- slide 11
TB = read("results/round2/R6_variance/r6_theta_build_comparison.csv")
if TB is not None:
    T = TB.set_index("sample_id")
    for sid in T.index:
        add(11, f"theta1 on {sid}, current morphology build", T.loc[sid, "v2_theta1_raw"],
            "results/round2/R6_variance/r6_theta_build_comparison.csv",
            f"v2_theta1_raw where sample_id={sid}")
    add(11, "theta1 on NCBI785, round-1 morphology build", T.loc["NCBI785", "v1_theta1_raw"],
        "results/round2/R6_variance/r6_theta_build_comparison.csv",
        "v1_theta1_raw where sample_id=NCBI785")
    add("A2", "between-slide spread of theta1, current build",
        T.v2_theta1_raw.max() - T.v2_theta1_raw.min(),
        "results/round2/R6_variance/r6_theta_build_comparison.csv",
        "max-min of v2_theta1_raw")
    add("A2", "between-slide spread of theta1, round-1 build",
        T.v1_theta1_raw.max() - T.v1_theta1_raw.min(),
        "results/round2/R6_variance/r6_theta_build_comparison.csv",
        "max-min of v1_theta1_raw")

VT = read("results/round2/R6_variance/r6_variance_by_task.csv")
if VT is not None:
    V = VT.set_index("task")
    for t in ("CCRCC", "LYMPH_IDC"):
        add(11, f"between-donor variance share, {t}", V.loc[t, "frac_donor"],
            "results/round2/R6_variance/r6_variance_by_task.csv", f"frac_donor where task={t}")
    add(11, "donors in CCRCC", V.loc["CCRCC", "donors"],
        "results/round2/R6_variance/r6_variance_by_task.csv", "donors where task=CCRCC")
    add(11, "smallest within-slide variance share over the ten tasks", VT.frac_spot.min(),
        "results/round2/R6_variance/r6_variance_by_task.csv", "min frac_spot")
    add(11, "largest within-slide variance share over the ten tasks", VT.frac_spot.max(),
        "results/round2/R6_variance/r6_variance_by_task.csv", "max frac_spot")

PB = read("results/round2/R6_variance/r6_pooled_between_donor.csv")
if PB is not None:
    wp = PB[PB.definition.str.startswith("well-powered")]
    if len(wp):
        add(11, "pooled between-donor share over the well-powered tasks", wp.value.iloc[0],
            "results/round2/R6_variance/r6_pooled_between_donor.csv",
            "value where definition starts with 'well-powered'")

DA = read("results/round2/R5b_audit/donor_audit.csv")
if DA is not None:
    st = DA.donor_label_status.astype(str)
    add(11, "samples audited", len(DA),
        "results/round2/R5b_audit/donor_audit.csv", "row count")
    for key, label in (("verified", "samples with verified donor labels"),
                       ("unverifiable", "samples whose donor labels are unverifiable"),
                       ("contradicted", "samples whose donor labels are contradicted")):
        add(11, label, int(st.str.contains(key).sum()),
            "results/round2/R5b_audit/donor_audit.csv",
            f"count donor_label_status containing '{key}'")

R7 = read("results/round2/R7_pergene/r7_correlations_task_centred.csv")
if R7 is not None:
    for _, r in R7.iterrows():
        add(11, f"within-task correlation, {r.x} against {r.y}", r.within_task,
            "results/round2/R7_pergene/r7_correlations_task_centred.csv",
            f"within_task where x={r.x} and y={r.y}")

CFN = read("results/round2/R5c_leak/r5d_idc_partner_confusion.csv")
if CFN is not None:
    add(4, "share of TENX slide confusion landing on the partner slide",
        CFN.onto_partner.sum() / CFN.off_diag.sum(),
        "results/round2/R5c_leak/r5d_idc_partner_confusion.csv",
        "sum onto_partner / sum off_diag")
    add(4, "that share at chance", CFN.expected_at_chance.iloc[0],
        "results/round2/R5c_leak/r5d_idc_partner_confusion.csv", "expected_at_chance")

# ----------------------------------------------------------------- slide A1
PH = read("results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv")
if PH is not None:
    H_ = PH.set_index("task")
    add("A1", "PAAD panel intersection", H_.loc["PAAD", "panel_intersection"],
        "results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv",
        "panel_intersection where task=PAAD")
    add("A1", "PAAD largest single-sample panel", H_.loc["PAAD", "panel_max"],
        "results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv", "panel_max where task=PAAD")
    add("A1", "IDC panel span between the smallest and largest sample panels",
        H_.loc["IDC", "panel_max"] - H_.loc["IDC", "panel_min"],
        "results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv",
        "panel_max - panel_min where task=IDC")

LS = read("results/round2/R2_fold_hvg/r2_leakage_summary.csv")
if LS is not None:
    add("A1", "mean gene-selection effect over tasks", LS.d_within.mean(),
        "results/round2/R2_fold_hvg/r2_leakage_summary.csv", "mean d_within")
    add("A1", "largest gene-selection effect", LS.d_within.max(),
        "results/round2/R2_fold_hvg/r2_leakage_summary.csv", "max d_within")
    add("A1", "genes shared between the shipped and training-only lists, mean",
        LS.shared.mean(),
        "results/round2/R2_fold_hvg/r2_leakage_summary.csv", "mean shared")
    add("A1", "genes shared on PRAD", LS.set_index("task").loc["PRAD", "shared"],
        "results/round2/R2_fold_hvg/r2_leakage_summary.csv", "shared where task=PRAD")

RS = read("results/round2/R2_fold_hvg/r2_rank_supplement.csv")
if RS is not None:
    add("A1", "Spearman between the fold ranking and the all-spot ranking",
        RS.spearman_rank.mean(),
        "results/round2/R2_fold_hvg/r2_rank_supplement.csv", "mean spearman_rank")

# ----------------------------------------------------------------- slide A2
CD = read("results/tailored/counts/count_diagnostics.csv")
if CD is not None:
    def flag(col, frame=None):
        f = CD if frame is None else frame
        return f[col].astype(str).str.lower().isin(["true", "1"])
    ok = CD[flag("both_converged")]
    # Counted among the converged fits, not over all 500 rows: over all rows the
    # NB-beats-Poisson count is 481, and the figure the deck quotes (478) is the
    # one restricted to pairs where both fits converged.
    add("A2", "gene-task pairs where NB beats Poisson",
        int((flag("nb_beats_poisson") & flag("both_converged")).sum()),
        "results/tailored/counts/count_diagnostics.csv",
        "count nb_beats_poisson among both_converged")
    add("A2", "gene-task pairs with both fits converged", int(len(ok)),
        "results/tailored/counts/count_diagnostics.csv", "count both_converged")
    # NOTE, and this one does not reconcile. Round 1 reported ZINB preferred on
    # 14 of 474 after excluding 14 NB fits the library had falsely flagged as
    # converged. The stored columns give 28 of 488, and 34 of all 500; the
    # exclusion RULE is not a column in this file, so 14/474 cannot be
    # re-derived here. What the file supports is recorded; the deck's figure is
    # left for whoever holds round 1's exclusion criterion to restate.
    add("A2", "gene-task pairs where ZINB beats NB, stored flags",
        int((flag("zinb_preferred") & flag("both_converged")).sum()),
        "results/tailored/counts/count_diagnostics.csv",
        "count zinb_preferred among both_converged")
    add("A2", "median AIC change from NB to ZINB", ok.delta_aic.median(),
        "results/tailored/counts/count_diagnostics.csv", "median delta_aic")
    add("A2", "smallest Fano factor over all gene-task pairs", CD.fano.min(),
        "results/tailored/counts/count_diagnostics.csv", "min fano")

ACC = sorted(glob.glob(f"{ROOT}/results/round2/R1b_heads/acceptance__*__f64.csv"))
if ACC:
    A = pd.concat([pd.read_csv(f) for f in ACC], ignore_index=True)
    f64 = A[A.solver.astype(str).str.contains("f64")]
    if len(f64):
        add("A2", "worst float64 three-head identity residual", f64.value.max(),
            "results/round2/R1b_heads/acceptance__*__f64.csv", "max value, f64 family")
    f32 = A[~A.solver.astype(str).str.contains("f64")]
    if len(f32):
        add("A2", "worst float32 identity residual", f32.value.max(),
            "results/round2/R1b_heads/acceptance__*__f64.csv", "max value, float32 families")

# ---------------------------------------------------------------------- write
D = pd.DataFrame(rows)[["slide", "label", "value", "source_file", "source_column_or_query"]]
assert not D.duplicated(subset=["slide", "label"]).any(), "duplicated slide/label pair"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
D.to_csv(OUT, index=False)

with open(f"{ROOT}/results/summary/PROVENANCE__deck_numbers.txt", "w") as f:
    f.write("Deck numbers, single source of truth\n"
            f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'NA')}\n"
            f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
            "script          : code/scripts/build_deck_numbers.py\n"
            f"command_line    : {' '.join(sys.argv)}\n"
            f"rows            : {len(D)}\n"
            f"slides covered  : {sorted(set(map(str, D.slide)))}\n"
            f"sources missing : {missing or 'none'}\n"
            "out of scope    : slide 7 is a literature slide; its figures come from\n"
            "                  published papers, not this repository, and are absent\n"
            "plan            : deck_figures_and_repo_update.md section 1.3\n")

print(f"wrote {OUT} with {len(D)} rows")
print(D.groupby("slide").size().to_string())
if missing:
    print("\nSOURCES MISSING (rows for these were skipped):")
    for m in missing:
        print("   ", m)
print(f"\ndistinct source files: {D.source_file.nunique()}")
