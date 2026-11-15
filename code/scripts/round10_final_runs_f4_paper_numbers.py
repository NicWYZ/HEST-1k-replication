"""Round 10, track final-runs, F4 (plan 5e.6): the numbers table of the paper.

Writes results/round10/final_runs/F4/paper_numbers.csv with one row per number the writing plan's sections S2 to S6
quote (docs/round10/tracks/ledger/round10_writing_plan.md), keyed by the findings survey's identifiers
(docs/round10/00_prep/round10_findings_survey.md, D, A, B and E) and by the ledger's S6 identifiers, with the final-runs
value beside an earlier round's where the final runs reproduce it, and rows for V, the institution axis and F4's readings.
Every value is read from a committed file of the clone by its selector; nothing is typed.

Columns: key, result_id, paper_section, quantity, value, file, selector, stage, commit.
`commit` is the last commit that touched `file` (git log -1 -- file). Selector grammar:
  <filters> -> <column>          the column of the one row matching every filter (an error if not exactly one row)
  count: <filters>               the number of rows matching
  sum|min|max|median: <filters> -> <column>
  json: a.b.c                    a key path into a JSON file
  re: <pattern>                  the first group of the first match in a text file
  expr: <python expression>      over earlier rows' values, written {key}
Filters are `col=value` (string or numeric equality), `col!=value`, `col<value`, `col>value`, joined by `&`; an empty
filter selects every row.

usage: round10_final_runs_f4_paper_numbers.py <clone> <out_csv> [--check]
"""
import json, os, re, subprocess, sys
import numpy as np, pandas as pd

F2T = "results/round10/final_runs/F2/report_tables/"
F2A = "results/round10/final_runs/F2/aggregate/"
F3A = "results/round10/final_runs/F3/aggregate/"
F4A = "results/round10/final_runs/F4/aggregate/"
F1A = "results/round10/final_runs/F1/aggregate/"
ROWS = []


def row(key, rid, sec, qty, f, sel, stage):
    ROWS.append(dict(key=key, result_id=rid, paper_section=sec, quantity=qty, file=f, selector=sel, stage=stage))


HEST4 = ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]
CORPUS = ["kidney__Visium", "breast__Spatial_Transcriptomics", "bowel__Visium", "brain__Visium", "breast__Xenium", "lung__Xenium"]
TASKS11 = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES"] + CORPUS


def enc(t):
    return "pkg" if t == "ACS_STATES" else "uni_v2"


def sc(t):
    return "log_income" if t == "ACS_STATES" else "log1p"


# ---------------- S2, data ----------------
for st in ["verified", "unverifiable", "contradicted"]:
    row(f"D6.{st}", "D6", "S2", f"HEST donor audit, samples {st}", "results/round2/R5b_audit/donor_audit.csv", f"count: donor_label_status={st}", "r2")
row("D6.all", "D6", "S2", "HEST donor audit, samples audited", "results/round2/R5b_audit/donor_audit.csv", "count: ", "r2")
TL = F1A + "f1_task_list.csv"
row("F1.samples", "S2-corpus", "S2", "corpus audit, samples considered", TL, "sum:  -> samples", "F1")
row("F1.samples_in", "S2-corpus", "S2", "corpus audit, samples kept", TL, "sum:  -> samples_in", "F1")
for t in CORPUS + ["breast__Visium"]:
    for col in ["donors", "centers_in", "samples_in"]:
        row(f"F1.{t}.{col}", "S2-corpus", "S2", f"corpus task {t}, {col}", TL, f"task={t} -> {col}", "F1")
C0 = "results/round9/diagnostics/c0_shared_donor_factor.csv"
C0M = "results/round9/diagnostics/c0_task_medians.csv"
for t in HEST4:
    row(f"D10.{t}.pc1", "D10", "S2", f"{t} uni_v2, share of between-donor variance on the first PC (log(1+y))", C0, f"task={t}&encoder=uni_v2 -> pc1_share", "r9")
    row(f"D10.{t}.r", "D10", "S2", f"{t} uni_v2, |r| of the first PC with donor average expression", C0, f"task={t}&encoder=uni_v2 -> abs_r_pc1_avg_y", "r9")
    row(f"D10.{t}.skew", "D10", "S2", f"{t}, median skewness of donor means", C0M, f"task={t}&encoder=uni_v2 -> skew_meany", "r9")
R11C = F2T + "r11c_pc1_share.csv"
for t in [x for x in TASKS11 if x != "ACS_STATES"]:
    row(f"F2.pc1.{t}.log1p", "D10", "S2", f"{t} uni_v2, first-PC share on log(1+y), final runs", R11C, f"task={t}&encoder=uni_v2&scale=log1p -> pc1_share", "F2")
    s2 = "lognorm" if t in CORPUS else "norm_refit"
    row(f"F2.pc1.{t}.{s2}", "D10/D11", "S2", f"{t} uni_v2, first-PC share on the normalised scale ({s2}), final runs", R11C, f"task={t}&encoder=uni_v2&scale={s2} -> pc1_share", "F2")
NS = "results/round9/norm/norm_summary.csv"
row("D11.raw", "D11", "S2", "CCRCC first-PC share, unnormalised", NS, "task=CCRCC -> pc1_share_raw", "r9")
row("D11.norm", "D11", "S2", "CCRCC first-PC share, library-size normalised", NS, "task=CCRCC -> pc1_share_norm", "r9")
BH = "results/round9/between/between_head_medians.csv"
for t in HEST4:
    row(f"D12.{t}", "D12", "S2", f"{t} uni_v2, leave-one-donor-out median R2 of the donor mean, pooled head", BH, f"task={t}&encoder=uni_v2&design=lodo -> R2_pooled", "r9")
row("D12.depth", "D12", "S2", "CCRCC, median R2 of the donor mean on a depth proxy", "results/round9/stud/probe_depth_auxiliary_medians.csv", "task=CCRCC -> R2_depth", "r9")
for t in CORPUS:
    row(f"F1.D12.{t}", "D12", "S2", f"{t} uni_v2 log(1+y), leave-one-donor-out median R2 of the donor mean, final runs", F1A + "f1_d12.csv", f"name={t}__uni_v2&scale=log1p -> R2_loo_const_median", "F1")
AD = "results/round9/stud/atypical_donor_diagnostics.csv"
row("D13.z", "D13", "S2", "INT5 z of average expression (CCRCC)", AD, "task=CCRCC -> z_avg_y", "r9")
row("D13.rank_pred", "D13", "S2", "INT5 rank of prediction outlyingness of 24", AD, "task=CCRCC -> rank_pred_outlyingness", "r9")
row("D13.rank_emb", "D13", "S2", "INT5 rank of embedding outlyingness of 24", AD, "task=CCRCC -> rank_emb_outlyingness", "r9")
row("D13.share", "D13", "S2", "CCRCC, share of genes whose largest residual share is INT5's", "results/round9/fewcluster/hest/i24_task_summary.csv", "task=CCRCC&encoder=uni_v2 -> frac_top_argmax", "r9")
D13F = "results/round10/final_runs/F1/diagnostics/d13_donor_diagnostics__r3_CCRCC_uni_v2.csv"
row("F1.D13.z", "D13", "S2", "INT5 z of average expression, final runs", D13F, "donor_id=INT5 -> z_avg_y", "F1")
row("F1.D13.rank_pred", "D13", "S2", "INT5 rank of prediction outlyingness, final runs", D13F, "donor_id=INT5 -> rank_pred_out", "F1")
row("F1.D13.rank_emb", "D13", "S2", "INT5 rank of embedding outlyingness, final runs", D13F, "donor_id=INT5 -> rank_emb_out", "F1")
N3 = "results/round9/newtopic/n3_predictions_scored.md"
row("D14.enc", "D14", "S2", "CCRCC median within-slide correlation between two encoders' predictions", N3, r"re: between two encoders' predictions is ([0-9.]+) on CCRCC", "r9")
row("D14.lab", "D14", "S2", "CCRCC median within-slide correlation of predictions with labels", N3, r"re: (0\.149)", "r9")

# ---------------- S3, prediction sets ----------------
A1 = "docs/round03/i01/exec/round3_A1_stage_report.md"
for d in ["random", "slide_out", "donor", "patient"]:
    row(f"A1.{d}", "A1", "S3", f"spot-level split conformal coverage, absolute score, design {d}", A1, rf"re: \| `{d}` \| `abs` \| ([0-9.]+) \|", "r3")
A3 = "results/round3/A3_report_numbers.csv"
row("A2.unit", "A2", "S3", "coverage calibrating on held-out donors", A3, "name=a2b_cov_C_unit -> value", "r3")
row("A2.block", "A2", "S3", "coverage calibrating on spatial blocks", A3, "name=a2b_cov_C_block -> value", "r3")
row("A2.cells", "A2", "S3", "cells with block below unit", A3, "name=a2b_n_block_below_unit -> value", "r3")
row("A2.n", "A2", "S3", "cells", A3, "name=a2b_n_cells -> value", "r3")
row("A3.auc", "A3", "S3", "minimum held-out AUC separating calibration and test slides", A3, "name=a3_w1_auc_holdout_min -> value", "r3")
row("A3.neff", "A3", "S3", "median effective calibration size, percent", A3, "name=a3_w1_neff_pct_median -> value", "r3")
A4 = "results/round3/A4_scores/a4b_summary.csv"
row("A4.hcp", "A4", "S3", "HCP coverage at K = 10, CCRCC", A4, "metric=coverage_mean&scope=donor_set=24 arm=K10 method=hcp -> value", "r3")
row("A4.ratio", "A4", "S3", "HCP width over the pooled quantile's at K = 10", A4, "metric=width_ratio_over_pooled&scope=donor_set=24 arm=K10 method=hcp -> value", "r3")
row("A4.pooled", "A4", "S3", "pooled quantile coverage at K = 10", A4, "metric=coverage_mean&scope=donor_set=24 arm=K10 method=pooled -> value", "r3")
row("A4.ratio20", "A4", "S3", "HCP width over pooled at K = 20", "results/round4/conformal/C3_real/c3_report_numbers.csv", "prediction=C3.1&quantity=hcp/pooled mean width, mean over encoders&scope=CCRCC alpha=0.1 K=20 -> value", "r4")
T02 = F3A + "t02_map_by_task_p103_methods_alpha01.csv"
for t in HEST4:
    row(f"F3.A4.{t}", "A4", "S3", f"{t} uni_v2 log(1+y), HCP coverage at K = 10, o = 0, final runs", T02, f"task={t}&encoder=uni_v2&scale=log1p&part=1&method=hcp&K=10&o=0 -> coverage_mean", "F3")
A4N = "results/round3/A4_scores/a4_report_numbers.csv"
row("A5.cqr", "A5", "S3", "CQR width at matched 0.90 coverage", A4N, "name=width_mean_at_cov90_cqr&scope=subset cqr_matched -> value", "r3")
row("A5.abs", "A5", "S3", "absolute score width at matched 0.90 coverage", A4N, "name=width_mean_at_cov90_abs&scope=subset cqr_matched -> value", "r3")
row("A5.top_abs", "A5", "S3", "top-decile coverage, absolute score", A4N, "name=top_decile_coverage_abs&scope=subset cqr_matched, all designs -> value", "r3")
row("A5.top_cqr", "A5", "S3", "top-decile coverage, CQR", A4N, "name=top_decile_coverage_cqr&scope=subset cqr_matched, all designs -> value", "r3")
T06 = F3A + "t06_item7_scores_margins.csv"
for t in HEST4:
    for s in ["cqr", "scaled_clip", "nb_conformal"]:
        row(f"F3.A5.{t}.{s}", "A5", "S3", f"{t}, width ratio of {s} to the absolute score, within_plain o = 9, final runs", T06, f"task={t}&method=within_plain&o=9&score={s} -> ratio", "F3")
W5 = "results/round5/conformal/W5_map/w5_report_numbers.csv"
for k, q, t, p, K, o in [("A6.ghcp_lo", "ghcp/hcp width", "CCRCC", 1, 10, 10), ("A6.ghcp_hi", "ghcp/hcp width", "INDIANA_KIDNEY", 1, 10, 3),
                         ("A6.cov_lo", "ghcp coverage min over o", "INDIANA_KIDNEY", 1, 10, -1), ("A6.cov_hi", "ghcp coverage max over o", "INDIANA_KIDNEY", 1, 10, -1),
                         ("A6.wf_lo", "within_full/hcp width", "CCRCC", 1, 10, 100), ("A6.wf_hi", "within_full/hcp width", "INDIANA_KIDNEY", 1, 10, 15),
                         ("A6.k12", "ghcp/hcp width", "CCRCC", 2, 12, 5), ("A6.k20", "ghcp/hcp width", "CCRCC", 2, 20, 5)]:
    row(k, "A6", "S3", f"{t}, {q}, part {p}, K = {K}, o = {o}", W5, f"quantity={q}&task={t}&part={p}&K={K}&o={o}&alpha=0.1 -> value", "r5")
T01 = F3A + "t01_map_p103.csv"
for t, p in [("CCRCC", 1), ("LUNG_XENIUM", 1)]:
    row(f"F3.A6.{t}.min", "A6", "S3", f"{t}, smallest margin of hcp over within_full across o from 9 (P10.3 part 1)", T01, f"min: task={t}&part={p} -> margin", "F3")
row("F3.A6.IK.min", "A6", "S3", "INDIANA_KIDNEY, smallest ratio within_full over within_plain (P10.3 part 2)", T01, "min: task=INDIANA_KIDNEY&part=2 -> margin", "F3")
row("F3.A6.IK.max", "A6", "S3", "INDIANA_KIDNEY, largest ratio within_full over within_plain (P10.3 part 2)", T01, "max: task=INDIANA_KIDNEY&part=2 -> margin", "F3")
row("A7.sim", "A7", "S3", "GHCP simulation values reproduced", "docs/round04/i02/conformal/round4_conf_final_report.md", r"re: at ([0-9]+) of 254 values", "r4")
LB = "results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv"
for K in range(4, 9):
    row(f"A8.K{K}", "A8", "S3", f"coverage floor of an a.s. finite method at K = {K}", LB, f"alpha=0.1&K={K} -> min_coverage_any_valid", "r4")
SS = "results/round9/stud/stud_summary.csv"
row("A9.hcp", "A9", "S3", "CCRCC o = 3, HCP half-width", SS, "task=CCRCC&o=3&method=hcp -> hw", "r9")
row("A9.oracle", "A9", "S3", "CCRCC o = 3, oracle-studentized half-width", SS, "task=CCRCC&o=3&method=oracle -> hw", "r9")
row("A9.gain", "A9", "S3", "CCRCC o = 3, width bought by oracle studentizing, 1 - oracle/hcp", "derived", "expr: 1 - {A9.oracle}/{A9.hcp}", "r9")
row("A10.hcp", "A10", "S3", "INT5 HCP coverage at o = 3", AD, "task=CCRCC -> hcp_cov_o3", "r9")
SP = "results/round9/stud/stud_per_donor_coverage.csv"
row("A10.xgene", "A10", "S3", "INT5 cross-gene studentized coverage at o = 3", SP, "task=CCRCC&o=3&method=xgene&target=INT5 -> coverage", "r9")
row("A10.int10", "A10", "S3", "INT10 cross-gene studentized coverage at o = 3 (the set's lowest)", SP, "task=CCRCC&o=3&method=xgene&target=INT10 -> coverage", "r9")
row("A10.min", "A10", "S3", "lowest per-donor coverage of the cross-gene set at o = 3, CCRCC", SP, "min: task=CCRCC&o=3&method=xgene -> coverage", "r9")
T09 = F3A + "t09_institution_fr8.csv"
row("INST.donor", "institution", "S3", "kidney Visium, donor-level HCP pooled, median coverage over 5 centers (FR8 clause 1)", T09, "clause=1 -> value", "F3")
row("INST.center", "institution", "S3", "kidney Visium, HCP over centers, median coverage (FR8 clause 2)", T09, "clause=2 -> value", "F3")
row("INST.S0006", "institution", "S3", "S0006 coverage under donor-level HCP pooled", T09, r"re: S0006:([0-9.]+)", "F3")
S6B = F4A + "f4_s0006_by_center.csv"
row("F4.S0006.resid", "institution", "S3", "S0006 median |y - f| (uni_v2 log1p)", S6B, "encoder=uni_v2&scale=log1p&center_unit=S0006 -> med_abs_resid", "F4")
row("F4.S0006.others", "institution", "S3", "largest other center's median |y - f| (uni_v2 log1p)", S6B, "max: encoder=uni_v2&scale=log1p&center_unit!=S0006 -> med_abs_resid", "F4")

# ---------------- S4, valid inference ----------------
R10 = F2T + "r10_buy_uni_v2_primary_n8.csv"
for t in TASKS11:
    row(f"B7.{t}", "B7", "S4", f"{t}, median width ratio fix1/classical, theta3, n_L = 8", R10, f"task={t}&estimand=theta3 -> median_wr_fix1", "F2")
    row(f"B4.{t}", "B4", "S4", f"{t}, Spearman over genes of fix1's width ratio with R2_c, theta3, n_L = 8", R10, f"task={t}&estimand=theta3 -> rho_wr_fix1_R2c", "F2")
    row(f"B4p.{t}", "B4", "S4", f"{t}, Spearman over genes of fix1's width ratio with spot Pearson, theta3, n_L = 8", R10, f"task={t}&estimand=theta3 -> rho_wr_fix1_pearson", "F2")
R10B = F2T + "r10b_d9_by_task.csv"
for t in [x for x in TASKS11 if x not in ("ACS_STATES", "CCRCC_merged")]:
    row(f"D9.{t}", "D9", "S4", f"{t} uni_v2 log(1+y), median ratio of donor-clustered to iid SE", R10B, f"task={t}&encoder=uni_v2&scale=log1p -> median", "F2")
R07 = F2T + "r07_limits_ranges.csv"
for arm, lab in [("r4_none|textbook_t|fpc|lin", "control, no coefficient"), ("r4_a_b1|textbook_t|fpc|lin", "same-sample tuning a_b1"),
                 ("r4_c_crossfit_design|textbook_t|fpc|lin|xf", "cross-fitted rule c"), ("kluger_ptd|cluster_boot", "Kluger cluster bootstrap")]:
    for n in [4, 8, 16]:
        row(f"B5.{arm.split('|')[0]}.n{n}", "B5/S6-1", "S4", f"{lab}, median over cells of median coverage, n_L = {n}", R07, f"arm={arm}&n={n} -> median", "F2")
R03B = F2T + "r03b_bootstrap_ranges.csv"
for arm in ["boot_pairs_pct|boot", "boot_wild_webb_t|boot", "boot_raowu_t|boot"]:
    for n in [4, 8, 16]:
        row(f"S6-2.{arm.split('|')[0]}.n{n}", "S6-2", "S6", f"{arm.split('|')[0]}, median coverage, n_L = {n}", R03B, f"arm={arm}&n={n} -> median", "F2")
        row(f"S6-2.{arm.split('|')[0]}.n{n}.wr", "S6-2", "S6", f"{arm.split('|')[0]}, median width ratio to fix1, n_L = {n}", R03B, f"arm={arm}&n={n} -> median_width_ratio_to_fix1", "F2")
R08 = F2T + "r08_regimeB_ranges.csv"
for form in ["C_fix1", "C_ppi", "C_classical"]:
    for col in ["ev_median", "ev_min", "ev_max", "cov_min", "cov_max"]:
        row(f"B6.{form}.{col}", "B6/S6-4", "S4", f"regime B form C {form}, {col} over 736 cells", R08, f"group=all&form={form} -> {col}", "F2")
SW = F2A + "f2_switch_decision.json"
row("B10.switch.min", "B10", "S4", "smallest median E(V_w)/Var over cells with n_L >= 6", SW, "json: min_median", "F2")
row("B10.switch.cells", "B10", "S4", "cells with n_L >= 6", SW, "json: cells", "F2")
R05B = F2T + "r05b_frac_V_neg_by_n.csv"
for n in [6, 8, 16]:
    row(f"B10.vneg.n{n}", "B10", "S4", f"median share of draws with V < 0, n_L = {n}", R05B, f"n={n} -> median", "F2")
FR1 = F1A + "f1_fr1.csv"
for t in HEST4 + ["ACS_STATES"]:
    row(f"B10.fr1.{t}", "B10", "S4", f"{t}, round 5's interval (with lin) over Williams' W_within at n_L = 8", FR1, f"task={t} -> ratio_R5_lin_over_W_within", "F1")
R13 = F2T + "r13_p10_1.csv"
for t in HEST4:
    row(f"B10.p101.{t}.r10", "B10", "S4", f"{t}, cross-fitted form with V_w, coverage at n_L = 8 (P10.1 part 1)", R13, f"task={t} -> coverage_r10", "F2")
    row(f"B10.p101.{t}.r5", "B10", "S4", f"{t}, round 5's row", R13, f"task={t} -> coverage_r5", "F2")

# ---------------- S5, how many donors ----------------
R01 = F2T + "r01_regimeA_uni_v2_primary.csv"
for t in TASKS11:
    for arm, lab in [("classical|fpc", "classical"), ("fix1|fpc", "fix1"), ("xf2_r5|V_w", "xf2, V_w")]:
        row(f"B8.{t}.{lab}", "B8/B11", "S5", f"{t}, median coverage of {lab}, theta3, n_L = 8", R01, f"task={t}&estimand=theta3&n=8 -> cov__{arm}", "F2")
R09 = F2T + "r09_shortfall_uni_v2_primary_n8.csv"
for t in TASKS11:
    for col in ["median_kappa_e", "kappa_sup", "share_beyond_sup", "median_Gstar_e"]:
        row(f"B13.{t}.{col}", "B13", "S5", f"{t}, theta3, n_L = 8, {col}", R09, f"task={t}&estimand=theta3 -> {col}", "F2")
R09B = F2T + "r09b_shortfall_correlations.csv"
for g in ["HEST_ACS", "corpus"]:
    row(f"B13.rho.{g}", "B13", "S5", f"{g}, median Spearman of fix1 coverage with kappa(e) over cells", R09B, f"group={g} -> rho_cov_fix1_kappa_e__median", "F2")
T12 = F3A + "t12_regcomp_summary_by_task.csv"
for t in HEST4 + ["CCRCC_merged", "ACS_STATES"]:
    row(f"E1.{t}.n", "E1", "S5", f"{t}, regime B vs A comparisons, fix1, theta3, c = 10", T12, f"task={t}&scale={sc(t)}&estimand=theta3&pair=fix1&c=10 -> n", "F3")
    row(f"E1.{t}.narrow", "E1", "S5", f"{t}, comparisons with regime B narrower", T12, f"task={t}&scale={sc(t)}&estimand=theta3&pair=fix1&c=10 -> B_narrower", "F3")
    row(f"E1.{t}.ratio", "E1", "S5", f"{t}, median width ratio B over A", T12, f"task={t}&scale={sc(t)}&estimand=theta3&pair=fix1&c=10 -> median_ratio_mean_width", "F3")
RC = "results/round10/final_runs/F3/regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json"
row("E1.r10f3a.n", "E1", "S5", "R10-F3a comparisons (fix1, theta3, c = 10)", RC, "json: r10f3a.primary.n", "F3")
row("E1.r10f3a.narrow", "E1", "S5", "R10-F3a comparisons with regime B narrower", RC, "json: r10f3a.primary.B_narrower", "F3")
row("E1.r10f3a.ratio", "E1", "S5", "R10-F3a median width ratio", RC, "json: r10f3a.primary.median_ratio", "F3")
MRG = F4A + "f4_regcomp_comparisons_merged.csv"
row("F4.mu.n", "E1", "S5", "all-spot mu, cost-matched fix1 comparisons, HEST and corpus", MRG, "count: estimand=mu&pair=fix1&mu_spots=all", "F4")
row("F4.mu.narrow", "E1", "S5", "all-spot mu, comparisons with regime B narrower", MRG, "count: estimand=mu&pair=fix1&mu_spots=all&median_ratio_mean_width<1", "F4")
ACSJ = F4A + "f4_acs_summary.json"
row("F4-3.share", "E1", "S5", "ACS by state, share of unit-cost pairs with regime B narrower (F4-3)", ACSJ, "json: unit_cost_share_B_narrower_acs", "F4")
row("F4-3.pairs", "E1", "S5", "ACS by state, unit-cost pairs", ACSJ, "json: unit_cost_pairs_acs", "F4")
AL = "results/round10/final_runs/F4/readings/readings_alloc_v1/f4_alloc_by_task.csv"
for t in HEST4 + ["CCRCC_merged", "ACS_STATES"]:
    row(f"F4-3b.{t}", "E1", "S5", f"{t}, allocation factor mean(Mbar/M_g) of regime B (F4-3b)", AL, f"task={t} -> alloc_factor", "F4")
T16B = F3A + "t16b_V_side_by_side.csv"
for t in ["CCRCC", "ACS_STATES"]:
    for col in ["median_m_bounded", "median_m_unbounded", "median_coverage_at_bounded", "median_coverage_at_unbounded"]:
        row(f"V.{t}.{col}", "V/E1", "S5", f"{t} {enc(t)} {sc(t)}, lambda 0, {col} (F3, mu_J on HEST)", T16B, f"task={t}&encoder={enc(t)}&scale={sc(t)}&lambda=0 -> {col}", "F3")
BOXM = F4A + "f4_box_task_summary_merged.csv"
row("V.F4.cov_min_b", "V", "S5", "smallest median coverage at the bounded m, all rows, mu from all spots", BOXM, "min:  -> median_coverage_at_bounded", "F4")
row("V.F4.cov_max_b", "V", "S5", "largest median coverage at the bounded m", BOXM, "max:  -> median_coverage_at_bounded", "F4")
row("V.F4.cov_min_u", "V", "S5", "smallest median coverage at the unbounded m", BOXM, "min:  -> median_coverage_at_unbounded", "F4")
row("V.F4.cov_max_u", "V", "S5", "largest median coverage at the unbounded m", BOXM, "max:  -> median_coverage_at_unbounded", "F4")
BC = "results/round10/final_runs/F3/regimeB/aggregate_v1/box/f3_box_checks.json"
row("FR7.dev", "V/E1", "S5", "FR7, largest |coverage - 0.90| of regime B fix1 at m >= 6", BC, "json: fr7.clause1.max_abs_dev", "F3")
T21 = F3A + "t21_allocation_summary_over_encoders.csv"
for t in HEST4 + ["ACS_STATES"]:
    row(f"E2.{t}", "E2", "S5", f"{t}, median over encoders of the PP to classical optimal m ratio, theta3, n_L = 8", T21, f"task={t}&scale={sc(t)}&estimand=theta3&gene_scope=all&n_L=8 -> ratio_PP_over_classical_median", "F3")
T22 = F3A + "t22_balance_matched.csv"
for dom, s in [("tissue", "log1p"), ("census", "log_income")]:
    for dn in ["D0_classical", "D0_fix1", "D2_rej_t", "D2_rej_t_fix1", "cube_S4b", "cube_S4b_fix1"]:
        row(f"E3.{dom}.{dn}.cov", "E3/E5", "S5", f"{dom}, {dn}, coverage, n_L = 8, p_a = 0.1", T22, f"domain={dom}&scale={s}&n_L=8&p_a=0.1&dname={dn} -> coverage", "F3")
        row(f"E3.{dom}.{dn}.wr", "E3/E5", "S5", f"{dom}, {dn}, width over D0 classical, n_L = 8, p_a = 0.1", T22, f"domain={dom}&scale={s}&n_L=8&p_a=0.1&dname={dn} -> wr_D0cl", "F3")
MD = "results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv"
row("E4.cells", "E4", "S5", "weighting cells under rejective selection", MD, "count: design=D2", "r7")
row("E4.pi0", "E4", "S5", "cells with a cluster never accepted in the simulated draws", MD, "count: design=D2&n_columns_with_pi_zero>0", "r7")
row("E4.pairs", "E4", "S5", "cells with some pair never sampled together", MD, "count: design=D2&share_pairs_pgh_zero>0", "r7")
S4N = "results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv"
row("E6.lo", "E6", "S5", "k-center, classical coverage, theta3 CCRCC_merged hoptimus0", S4N, "name=S4.1_classical_coverage|theta3|CCRCC_merged|hoptimus0 -> value", "r7")
row("E6.hi", "E6", "S5", "k-center, classical coverage, theta3 CCRCC uni_v2", S4N, "name=S4.1_classical_coverage|theta3|CCRCC|uni_v2 -> value", "r7")
row("E6.pairs", "E6", "S5", "k-center, median share of pairs never sampled together, n_L = 8", S4N, "name=S4_share_pairs_pgh_zero_median|nL8 -> value", "r7")
T28 = F3A + "t28_takeall_vs_r9.csv"
for t in HEST4:
    for col in ["r9_cov_D0", "r9_cov_T0", "r9_wrD0_T0", "r10_cov_D0", "r10_cov_T0", "r10_wrD0_T0"]:
        row(f"E7.{t}.{col}", "E7", "S5", f"{t}, take-all k = 1, n_L = 8, {col}", T28, f"task={t}&k=1&n_L=8 -> {col}", "F3")
T31 = F3A + "t31_e8_on_grid_by_m.csv"
for t in HEST4 + ["kidney__Visium", "ACS_STATES"]:
    row(f"E8.{t}", "E8", "S5", f"{t}, regime B fix1 width over classical at m = 10, theta3", T31, f"task={t}&encoder={enc(t)}&scale={sc(t)}&estimand=theta3&m=10 -> regB_wr_fix1", "F3")
row("E8.nofinite", "E8", "S5", "on-grid rows with no finite set needing no further labels", F3A + "t30_e8_row_counts.csv", "task=ALL -> on_grid_rows_without_finite_noextra_set", "F3")
row("E8.m15", "E8", "S5", "rows at m = 15 where the overall set needs extra labels (all GHCP)", F4A + "f4_e8_m15_rows.csv", "count: overall_method=ghcp", "F4")

# ---------------- S6, limits ----------------
R02 = F2T + "r02_regimeA_grid_ranges.csv"
for arm in ["classical|fpc", "classical_nofpc|nofpc", "fix1|fpc", "fix1_nofpc|nofpc", "bh_t_fpc|own", "bh_t|own", "bh|own", "ctrl_perm_fix1|fpc", "ctrl_const_fix1|fpc"]:
    for n in [4, 8]:
        row(f"S6.{arm.split('|')[0]}.n{n}", {"classical_nofpc": "S6-3", "fix1_nofpc": "S6-3", "bh_t_fpc": "S6-7", "bh_t": "S6-7", "bh": "S6-7",
                                               "ctrl_perm_fix1": "S6-5", "ctrl_const_fix1": "S6-5"}.get(arm.split('|')[0], "S6-3"),
            "S6", f"{arm}, median over HEST and ACS cells of median coverage, n_L = {n}", R02, f"arm={arm}&group=HEST_ACS&n={n} -> median", "F2")
R12 = F2T + "r12_superpop_four_tasks.csv"
for t in HEST4 + ["ACS_STATES"]:
    for n in [8, 12]:
        row(f"S6-6.{t}.n{n}", "S6-6", "S6", f"{t}, fix1_nofpc coverage against the design target, theta3, n_L = {n}", R12, f"task={t}&encoder={enc(t)}&scale={sc(t)}&estimand=theta3&n={n} -> median_cov_fix1_nofpc", "F2")


_COMMIT, _TRACKED, _TABLES = {}, None, {}


def git_commit(clone, f):
    if f == "derived":
        return ""
    if f not in _COMMIT:
        _COMMIT[f] = subprocess.run(["git", "-C", clone, "--no-optional-locks", "log", "-1", "--format=%h", "--", f],
                                    capture_output=True, text=True).stdout.strip()
    return _COMMIT[f]


def tracked(clone, f):
    global _TRACKED
    if _TRACKED is None:
        _TRACKED = set(subprocess.run(["git", "-C", clone, "--no-optional-locks", "ls-files"], capture_output=True, text=True).stdout.split("\n"))
    return f == "derived" or f in _TRACKED


def table(p):
    if p not in _TABLES:
        _TABLES[p] = pd.read_csv(p, dtype=str, keep_default_na=False)
    return _TABLES[p]


def mask(t, flt):
    m = np.ones(len(t), bool)
    for part in [p for p in flt.split("&") if p.strip()]:
        for op in ["!=", "<", ">", "="]:
            if op in part:
                c, v = part.split(op, 1); c = c.strip(); v = v.strip(); break
        col = t[c]
        num = pd.to_numeric(col, errors="coerce")
        try:
            fv = float(v); isnum = num.notna().any()
        except ValueError:
            fv = None; isnum = False
        if op == "=":
            m &= (np.isclose(num, fv) & num.notna()).to_numpy() if isnum else (col.astype(str) == v).to_numpy()
        elif op == "!=":
            m &= ~((np.isclose(num, fv) & num.notna()).to_numpy() if isnum else (col.astype(str) == v).to_numpy())
        elif op == "<":
            m &= (num < fv).to_numpy()
        else:
            m &= (num > fv).to_numpy()
    return m


def read(clone, r, done):
    f, sel = r["file"], r["selector"]
    if sel.startswith("expr:"):
        return float(eval(re.sub(r"\{([^}]+)\}", lambda mm: repr(done[mm.group(1)]), sel[5:]), {}))
    p = os.path.join(clone, f)
    if sel.startswith("json:"):
        d = json.load(open(p))
        for k in sel[5:].strip().split("."):
            d = d[k]
        return d
    if sel.startswith("re:"):
        mm = re.search(sel[3:].strip(), open(p, encoding="utf-8").read())
        if not mm:
            raise ValueError("no match")
        return float(mm.group(1))
    t = table(p)
    kind = None
    body = sel
    for k in ["count:", "sum:", "min:", "max:", "median:"]:
        if sel.startswith(k):
            kind = k[:-1]; body = sel[len(k):]
    flt, col = (body.split("->") + [None])[:2] if "->" in body else (body, None)
    m = mask(t, flt.strip())
    if kind == "count":
        return int(m.sum())
    x = pd.to_numeric(t.loc[m, col.strip()], errors="coerce")
    if kind is None:
        if m.sum() != 1:
            raise ValueError(f"{int(m.sum())} rows match")
        return float(x.iloc[0])
    if m.sum() == 0:
        raise ValueError("0 rows match")
    return float(getattr(x, kind)())


def main():
    clone, out = sys.argv[1], sys.argv[2]
    check = "--check" in sys.argv
    keys = [r["key"] for r in ROWS]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        raise SystemExit(f"duplicate keys {dup}")
    done, recs, errs = {}, [], []
    for r in ROWS:
        rr = dict(r)
        try:
            if not tracked(clone, r["file"]):
                raise ValueError("file not tracked")
            v = read(clone, r, done)
            done[r["key"]] = v
            rr["value"] = v
        except Exception as e:
            errs.append((r["key"], r["file"], r["selector"], repr(e)))
            rr["value"] = ""
        rr["commit"] = git_commit(clone, r["file"])
        recs.append(rr)
    D = pd.DataFrame(recs)[["key", "result_id", "paper_section", "quantity", "value", "file", "selector", "stage", "commit"]]
    summ = dict(rows=len(D), errors=len(errs), by_section=D.paper_section.value_counts().to_dict(), by_stage=D.stage.value_counts().to_dict())
    if check:
        for e in errs:
            print("ERR", *e)
        print(json.dumps(summ))
        return
    if errs:
        for e in errs:
            print("ERR", *e)
        raise SystemExit(f"{len(errs)} selectors failed")
    json.dump(summ, open(os.path.splitext(out)[0] + "_summary.json", "w"), indent=1)
    D.to_csv(out, index=False)
    print(json.dumps(summ))


if __name__ == "__main__":
    main()
