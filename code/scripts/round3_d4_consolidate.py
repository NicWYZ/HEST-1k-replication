#!/usr/bin/env python
"""Round 3, stage D4: consolidate the per-encoder tables into the section 13.7 deliverables and
compute every pooled number the D4 report quotes.

Stage: D4 (round3_execution_plan.md section 13.7). Every pooled figure in the hand-back -- means
over encoders, counts of cells meeting a condition, Spearman correlations, prediction verdicts --
is computed here into d4_pooled_numbers.csv and read back from it, never retyped. Run locally on
the per-encoder CSVs the Longleaf jobs produced.

Usage: round3_d4_consolidate.py <in_dir> <out_dir> <repo_root>
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

IN, OUT, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
ENCS = ["hoptimus0", "resnet50", "uni_v2"]
os.makedirs(OUT, exist_ok=True)
pool = []


def add(name, scope, value, n=None, note=""):
    pool.append(dict(quantity=name, scope=scope, value=value, n=n, note=note))


def cat(pattern):
    fs = sorted(glob.glob(f"{IN}/{pattern}"))
    assert fs, pattern
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True), [os.path.basename(f) for f in fs]


# ------------------------------------------------------------------ 1. the layout anchor
ANC, anc_files = cat("d4_layout_anchor__*.csv")
bp = pd.read_csv(f"{REPO}/results/summary/results_task.csv")
bp = bp[(bp["head"] == "pca_ridge") & (bp["task"] == "CCRCC")][["encoder", "pearson_mean",
                                                                "pearson_std", "n_splits"]]
bp = bp.rename(columns={"pearson_mean": "benchmark_pearson_committed_fixed",
                        "pearson_std": "benchmark_pearson_sd_fixed",
                        "n_splits": "benchmark_n_splits"})
ANC = ANC.drop(columns=["benchmark_pearson_committed", "benchmark_pearson_sd"]).merge(
    bp, on="encoder", how="left")
ANC["pearson_pooled_vs_benchmark_bench_layout"] = (ANC["pearson_pooled_bench_layout"]
                                                   - ANC["benchmark_pearson_committed_fixed"])
ANC["prediction8_pearson_move_under_0p01"] = ANC["pearson_within_slide_diff"].abs() < 0.01
ANC["prediction8_pearson_pooled_move_under_0p01"] = ANC["pearson_pooled_diff"].abs() < 0.01
ANC["prediction8_coverage_move_under_fold_dispersion"] = (
    ANC["coverage_diff_hest_minus_bench"].abs() < ANC["coverage_sd_across_folds_bench"])
ANC.to_csv(f"{OUT}/d4_layout_anchor.csv", index=False)

CHK, chk_files = cat("d4_layout_anchor_a1_check__*.csv")
CHK.to_csv(f"{OUT}/d4_layout_anchor_a1_check.csv", index=False)
FOLD, _ = cat("d4_layout_anchor_by_fold__*.csv")
FOLD.to_csv(f"{OUT}/d4_layout_anchor_by_fold.csv", index=False)
SS, _ = cat("d4_layout_spot_sets__*.csv")
SS.to_csv(f"{OUT}/d4_layout_spot_sets.csv", index=False)

add("anchor_of_anchor_checks_total", "3 encoders", int(len(CHK)))
add("anchor_of_anchor_checks_passed", "3 encoders", int(CHK.passed.sum()))
add("anchor_of_anchor_coverage_max_abs_diff", "3 encoders, coverage metrics only",
    float(CHK[CHK.metric.isin(["coverage", "coverage_mean", "coverage_sd", "miss_above",
                               "miss_below"])].max_abs_diff.max()),
    note="A1's committed CCRCC rows against the bench-layout arm of this script")
add("anchor_of_anchor_width_max_abs_diff", "3 encoders, width metrics",
    float(CHK[CHK.metric.isin(["width_mean", "width_sd"])].max_abs_diff.max()))
add("anchor_of_anchor_folds_unmatched", "3 encoders",
    int(CHK.n_folds_new_only.sum() + CHK.n_folds_a1_only.sum()))
for d in sorted(ANC.design.unique()):
    s = ANC[ANC.design == d]
    add(f"coverage_bench_layout_mean_over_encoders__{d}", "CCRCC, abs", float(s.coverage_bench_layout.mean()), 3)
    add(f"coverage_hest_layout_mean_over_encoders__{d}", "CCRCC, abs", float(s.coverage_hest_layout.mean()), 3)
    add(f"coverage_diff_mean_over_encoders__{d}", "CCRCC, abs", float(s.coverage_diff_hest_minus_bench.mean()), 3)
    add(f"coverage_diff_max_abs_over_encoders__{d}", "CCRCC, abs", float(s.coverage_diff_hest_minus_bench.abs().max()), 3)
    add(f"pearson_within_slide_diff_mean_over_encoders__{d}", "CCRCC, abs", float(s.pearson_within_slide_diff.mean()), 3)
    add(f"pearson_within_slide_diff_max_abs_over_encoders__{d}", "CCRCC, abs", float(s.pearson_within_slide_diff.abs().max()), 3)
    add(f"pearson_pooled_diff_max_abs_over_encoders__{d}", "CCRCC, abs", float(s.pearson_pooled_diff.abs().max()), 3)
add("prediction8_pearson_cells_under_0p01", "9 encoder-design cells, within-slide",
    int(ANC.prediction8_pearson_move_under_0p01.sum()), 9)
add("prediction8_coverage_cells_within_fold_dispersion", "9 encoder-design cells",
    int(ANC.prediction8_coverage_move_under_fold_dispersion.sum()), 9)
add("spot_sets_hest_only_spots", "CCRCC, 24 samples, 3 encoders", int(SS.n_hest_only.sum()))
add("spot_sets_bench_only_spots", "CCRCC, 24 samples, 3 encoders", int(SS.n_bench_only.sum()))
add("spot_sets_expression_identical_samples", "CCRCC, 24 samples x 3 encoders",
    int(SS.expression_identical.sum()), int(len(SS)))
add("spot_sets_max_abs_count_diff", "CCRCC 50 genes, shared barcodes",
    float(SS.max_abs_count_diff_50genes.max()))

# ------------------------------------------------------------------ 2. Indiana
IND, _ = cat("d4_indiana__*.csv")
IND.to_csv(f"{OUT}/d4_indiana.csv", index=False)
INDF, _ = cat("d4_indiana_by_fold__*.csv")
INDF.to_csv(f"{OUT}/d4_indiana_by_fold.csv", index=False)
INDC, _ = cat("d4_indiana_cells_by_fold__*.csv")
INDC.to_csv(f"{OUT}/d4_indiana_cells_by_fold.csv", index=False)
PG, _ = cat("d4_indiana_pergene__*.csv")
PG.to_csv(f"{OUT}/d4_indiana_pergene.csv", index=False)
PGC, _ = cat("d4_indiana_pergene_correlations__*.csv")
PGC.to_csv(f"{OUT}/d4_indiana_pergene_correlations.csv", index=False)
GL, _ = cat("d4_indiana_fold_genes__*.csv")
GL.drop_duplicates(subset=["task", "design", "fold", "repeat"]).to_csv(
    f"{OUT}/d4_indiana_fold_genes.csv", index=False)

for (d, m), s in IND.groupby(["design", "method"]):
    add(f"indiana_coverage_mean_over_encoders__{d}__{m}", "Indiana, abs, alpha 0.10",
        float(s.coverage_mean.mean()), 3)
    add(f"indiana_coverage_min_over_encoders__{d}__{m}", "Indiana", float(s.coverage_mean.min()), 3)
    add(f"indiana_coverage_max_over_encoders__{d}__{m}", "Indiana", float(s.coverage_mean.max()), 3)
    add(f"indiana_coverage_sd_across_folds_mean__{d}__{m}", "Indiana", float(s.coverage_sd.mean()), 3)
    add(f"indiana_width_mean_over_encoders__{d}__{m}", "Indiana", float(s.width_mean.mean()), 3)
    add(f"indiana_n_T_mean__{d}__{m}", "Indiana", float(s.n_T_mean.mean()), 3)
    add(f"indiana_n_C_mean__{d}__{m}", "Indiana", float(s.n_C_mean.mean()), 3)
hcp = IND[(IND.design == "a4b_k10") & (IND.method == "hcp_w3")]
pq_ = IND[(IND.design == "a4b_k10") & (IND.method == "pooled_quantile")]
add("indiana_a4b_hcp_finite_cells", "25 folds x 3 draws x 3 encoders",
    int(hcp.n_cells_finite.sum()), int(hcp.n_cells.sum()))
add("indiana_a4b_hcp_width_ratio_to_pooled", "mean over encoders",
    float((hcp.set_index("encoder").width_mean / pq_.set_index("encoder").width_mean).mean()), 3)
add("indiana_a4b_hcp_coverage_ge_0p90_encoders", "3 encoders",
    int((hcp.coverage_mean >= 0.90).sum()), 3)
don = IND[(IND.design == "donor") & (IND.method == "pooled_quantile")]
add("indiana_donor_coverage_in_0p85_0p88_encoders", "3 encoders, prediction 9's band",
    int(((don.coverage_mean >= 0.85) & (don.coverage_mean <= 0.88)).sum()), 3)
K = INDF[INDF.method == "hcp_w3"] if "method" in INDF else None
# the per-gene split penalty, and its correlation with the between-donor share
for x, y in (("random_minus_donor", "frac_donor"), ("random_minus_a4b_k10", "frac_donor")):
    s = PGC[(PGC.x == x) & (PGC.y == y)]
    if len(s):
        add(f"indiana_spearman__{x}__{y}", "3 encoders, mean", float(s.spearman.mean()), 3)
if "random_minus_donor" in PG:
    add("indiana_pergene_split_penalty_mean", "3 encoders x genes",
        float(PG.random_minus_donor.mean()), int(PG.random_minus_donor.notna().sum()))
    add("indiana_pergene_split_penalty_median", "3 encoders x genes",
        float(PG.random_minus_donor.median()))
if "frac_donor" in PG:
    add("indiana_frac_donor_median", "genes, between-donor variance share",
        float(PG.drop_duplicates("gene").frac_donor.median()),
        int(PG.drop_duplicates("gene").frac_donor.notna().sum()))
add("indiana_fold_gene_lists_with_50_genes", "55 selections",
    int((GL.drop_duplicates(subset=["design", "fold", "repeat"]).n_genes == 50).sum()),
    int(len(GL.drop_duplicates(subset=["design", "fold", "repeat"]))))
add("indiana_fold_genes_off_panel_total", "55 selections",
    int(GL.drop_duplicates(subset=["design", "fold", "repeat"]).n_off_panel.sum()))

# ------------------------------------------------------------------ 3. population_out
PO, _ = cat("d4_population_out__*.csv")
PO.to_csv(f"{OUT}/d4_population_out.csv", index=False)
POF, _ = cat("d4_population_out_by_fold__*.csv")
POF.to_csv(f"{OUT}/d4_population_out_by_fold.csv", index=False)
POC, _ = cat("d4_population_out_calibration_units__*.csv")
POC.to_csv(f"{OUT}/d4_population_out_calibration_units.csv", index=False)
POG, _ = cat("d4_population_out_fold_genes__*.csv")
POG.drop_duplicates(subset=["task", "design", "fold", "repeat"]).to_csv(
    f"{OUT}/d4_population_out_fold_genes.csv", index=False)
add("population_out_coverage_mean_over_encoders_both_directions", "KIDNEY_POP54, abs",
    float(PO.coverage_mean.mean()), 3)
for f_, s in POF.groupby("fold"):
    add(f"population_out_coverage_mean_over_encoders__{f_}", "KIDNEY_POP54",
        float(s.coverage.mean()), int(s.encoder.nunique()))
    add(f"population_out_miss_above_mean_over_encoders__{f_}", "KIDNEY_POP54",
        float(s.miss_above.mean()), int(s.encoder.nunique()))
    add(f"population_out_miss_below_mean_over_encoders__{f_}", "KIDNEY_POP54",
        float(s.miss_below.mean()), int(s.encoder.nunique()))
    add(f"population_out_width_mean_over_encoders__{f_}", "KIDNEY_POP54",
        float(s.width_mean.mean()), int(s.encoder.nunique()))
    add(f"population_out_n_T__{f_}", "KIDNEY_POP54, size-matched", float(s.n_T.mean()))
add("population_out_cells_at_or_under_0p70", "2 directions x 3 encoders, prediction 10",
    int((POF.coverage <= 0.70).sum()), int(len(POF)))

PR, _ = cat("d4_population_probe__*.csv")
PRA, _ = cat("d4_population_probe_adjustment__*.csv")
PR.to_csv(f"{OUT}/d4_population_probe.csv", index=False)
PRA.to_csv(f"{OUT}/d4_population_probe_adjustment.csv", index=False)
PRF, _ = cat("d4_population_probe_folds__*.csv")
PRF.to_csv(f"{OUT}/d4_population_probe_folds.csv", index=False)
for (proto, adj), s in PR.groupby(["protocol", "adjustment"]):
    add(f"probe_balanced_accuracy_mean_over_encoders__{proto}__{adj}", "population target",
        float(s.balanced_accuracy.mean()), 3)
for proto, s in PRA.groupby("protocol"):
    add(f"probe_fraction_above_chance_removed_mean__{proto}", "3 encoders",
        float(s.fraction_above_chance_removed.mean()), 3)
    add(f"probe_composition_explains_majority_encoders__{proto}", "3 encoders",
        int(s.composition_explains_majority.sum()), 3)

# ------------------------------------------------------------------ 4. breast
BR, _ = cat("d4_breast__*.csv")
BR.to_csv(f"{OUT}/d4_breast.csv", index=False)
BRF, _ = cat("d4_breast_by_fold__*.csv")
BRF.to_csv(f"{OUT}/d4_breast_by_fold.csv", index=False)
BST = []
for e in ENCS:
    p = f"{IN}/d4_breast_strata__{e}.csv"
    d = pd.read_csv(p)
    d.insert(0, "encoder", e)
    BST.append(d)
BST = pd.concat(BST, ignore_index=True)
BST.to_csv(f"{OUT}/d4_breast_strata.csv", index=False)
BRG, _ = cat("d4_breast_fold_genes__*.csv")
BRG.drop_duplicates(subset=["task", "design", "fold", "repeat"]).to_csv(
    f"{OUT}/d4_breast_fold_genes.csv", index=False)
for (d, m), s in BR.groupby(["design", "method"]):
    add(f"breast_coverage_mean_over_encoders__{d}__{m}", "BREAST_XENIUM, abs",
        float(s.coverage_mean.mean()), 3)
    add(f"breast_coverage_min_over_encoders__{d}__{m}", "BREAST_XENIUM", float(s.coverage_mean.min()), 3)
    add(f"breast_coverage_max_over_encoders__{d}__{m}", "BREAST_XENIUM", float(s.coverage_mean.max()), 3)
    add(f"breast_width_mean_over_encoders__{d}__{m}", "BREAST_XENIUM", float(s.width_mean.mean()), 3)
bd = BR[(BR.design == "donor") & (BR.method == "pooled_quantile")]
add("breast_donor_coverage_in_0p82_0p87_encoders", "3 encoders, prediction 11's band",
    int(((bd.coverage_mean >= 0.82) & (bd.coverage_mean <= 0.87)).sum()), 3)
st = BST[(BST.design == "donor") & (BST.stratum == "instrument_generation_by_sample")]
for lvl, s in st.groupby("level"):
    add(f"breast_donor_coverage_mean_over_encoders__instrument_{lvl}", "by sample",
        float(s.coverage.mean()), int(s.encoder.nunique()))
piv = st.pivot_table(index="encoder", columns="level", values="coverage")
add("breast_prototype_minus_production_coverage_mean", "3 encoders",
    float((piv["prototype"] - piv["production"]).mean()), 3)
add("breast_prototype_below_production_encoders", "3 encoders",
    int((piv["prototype"] < piv["production"]).sum()), 3)
for lvl, s in BST[(BST.design == "donor") & (BST.stratum == "disease")].groupby("level"):
    add(f"breast_donor_coverage_mean_over_encoders__disease_{lvl}", "BREAST_XENIUM",
        float(s.coverage.mean()), int(s.encoder.nunique()))
dg = BST[(BST.design == "donor") & (BST.stratum == "instrument_generation_by_donor_group")]
add("breast_donor_group_stratum_matches_sample_stratum", "coverage, 3 encoders x 2 levels",
    bool(np.allclose(sorted(dg.coverage.values), sorted(st.coverage.values))),
    note="no donor group spans both instrument generations, so the two readings partition the "
         "same cells; the difference between them is the unit count (2 against 13 groups "
         "rather than 3 against 15 samples), not the partition")

# ------------------------------------------------------------------ 5. task definitions
V = pd.read_csv(f"{IN}/d4_task_defs_validation.csv")
V.to_csv(f"{OUT}/d4_task_defs_validation.csv", index=False)
TS = pd.read_csv(f"{IN}/d4_task_def_samples.csv")
TS.to_csv(f"{OUT}/d4_task_def_samples.csv", index=False)
BI = pd.read_csv(f"{IN}/d4_barcode_integrity.csv")
BI.to_csv(f"{OUT}/d4_barcode_integrity.csv", index=False)
MS = pd.read_csv(f"{IN}/d4_morphology_summary.csv")
MS.to_csv(f"{OUT}/d4_morphology_summary.csv", index=False)
add("task_defs_written", "D4", int(len(V)))
add("task_defs_passing_relaxed_v1", "D4", int(V.v1_relaxed_error.isna().sum()), int(len(V)))
add("task_defs_passing_extension_schema", "D4", int(V.ext_schema_error.isna().sum()), int(len(V)))
add("barcode_integrity_samples_checked", "72 expansion + 32 benchmark", int(len(BI)))
add("barcode_integrity_samples_ok", "obs/var unique and one row per patch barcode",
    int((BI.obs_unique & BI.var_unique & BI.one_row_per_patch_barcode).sum()), int(len(BI)))
add("unpatched_fraction_median__kidney", "54 samples",
    float(TS[TS.task_def == "KIDNEY_POP54"].unpatched_fraction.median()), 54)
add("unpatched_fraction_max__kidney", "54 samples",
    float(TS[TS.task_def == "KIDNEY_POP54"].unpatched_fraction.max()), 54)
add("unpatched_fraction_median__breast", "18 samples",
    float(TS[TS.task_def == "BREAST_XENIUM"].unpatched_fraction.median()), 18)
add("unpatched_fraction_max__breast", "18 samples",
    float(TS[TS.task_def == "BREAST_XENIUM"].unpatched_fraction.max()), 18)
add("unpatched_fraction_median__indiana", "26 samples",
    float(TS[TS.task_def == "INDIANA_KIDNEY"].unpatched_fraction.median()), 26)
add("unpatched_fraction_median__ccrcc_anchor", "24 samples",
    float(TS[TS.task_def == "CCRCC_hest_layout"].unpatched_fraction.median()), 24)
add("morphology_half_width_source_counts", "54 kidney samples",
    json.dumps(MS.half_width_source.value_counts().to_dict()))
add("morphology_mean_nuclei_per_spot_median", "54 kidney samples",
    float(MS.mean_nuclei_per_spot.median()), 54)
add("morphology_samples_without_dead_class", "54 kidney samples",
    int((~MS.dead_class_present).sum()), 54)

POOL = pd.DataFrame(pool)
POOL.to_csv(f"{OUT}/d4_pooled_numbers.csv", index=False)
print(f"[write] {OUT}/d4_pooled_numbers.csv ({len(POOL)} rows)")
for f in sorted(os.listdir(OUT)):
    print("  ", f)
