"""Recompute every pooled number quoted in docs/round3_A3_stage_report.md from the committed tables.

Why. The numeric-claim gate confirms that a quoted value occurs in a cited file. A pooled statistic
(a Spearman correlation, an across-encoder mean of per-encoder rows, a count of cells meeting a
condition) occurs in no file, and a coincidental match elsewhere in a large table can make it
"pass" without being checked. This script computes each such number from the committed tables by
an explicit rule and writes it, with the rule, to one CSV the report cites.

Usage (repository root):
    python code/scripts/round3_a3_report_numbers.py
Writes results/round3/A3_report_numbers.csv with columns name, value, rule, source.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

R = Path("results/round3")
A2 = R / "A2_conditional"
A1 = R / "A1_coverage"
ENC3 = ["hoptimus0", "resnet50", "uni_v2"]
rows = []


def put(name, value, rule, source):
    rows.append({"name": name, "value": value, "rule": rule, "source": source})


# ---------------------------------------------------------------- A2b, the intervention
ui = pd.read_csv(A2 / "a2_unit_intervention.csv")
uf = ui[ui.scope == "fold"].copy()
a1 = pd.concat([pd.read_csv(A1 / f"a1_by_fold__{e}__main.csv").assign(encoder=e) for e in ENC3])
a1d = a1[(a1.design == "donor") & (a1.score == "abs")][["task", "label_set", "encoder", "fold", "coverage"]]
m = uf.merge(a1d, on=["task", "label_set", "encoder", "fold"], how="left", validate="one_to_one")
assert m.coverage.notna().all()
src = "A2_conditional/a2_unit_intervention.csv (scope=fold); A1_coverage/a1_by_fold__<enc>__main.csv"
put("a2b_n_cells", len(uf), "fold rows", src)
put("a2b_anchor_max_abs_diff", float((m.coverage__anchor_a1 - m.coverage).abs().max()), "max |anchor - A1 coverage|", src)
put("a2b_cov_C_unit", uf.coverage__C_unit.mean(), "mean over fold rows", src)
put("a2b_cov_C_block", uf.coverage__C_block.mean(), "mean over fold rows", src)
d = uf.coverage__C_unit - uf.coverage__C_block
put("a2b_diff_mean", d.mean(), "mean of C_unit - C_block", src)
put("a2b_diff_sd", d.std(), "sd (ddof=1) of C_unit - C_block over fold rows", src)
put("a2b_n_block_below_unit", int((d > 0).sum()), "count C_block < C_unit", src)
put("a2b_width_C_unit", uf.width_mean__C_unit.mean(), "mean over fold rows", src)
put("a2b_width_C_block", uf.width_mean__C_block.mean(), "mean over fold rows", src)
put("a2b_unit_minus_a1_mean", (m.coverage__C_unit - m.coverage).mean(), "mean C_unit - A1", src)
put("a2b_unit_minus_a1_sd", (m.coverage__C_unit - m.coverage).std(), "sd", src)
bm = m.coverage__C_block - m.coverage
put("a2b_block_minus_a1_mean", bm.mean(), "mean C_block - A1", src)
put("a2b_block_minus_a1_median", bm.median(), "median C_block - A1", src)
put("a2b_pct_block_minus_a1_in_010_020", 100 * bm.between(-0.20, -0.10).mean(), "% of cells with C_block - A1 in [-0.20,-0.10]", src)
put("a2b_pct_nC_unit_of_anchor", 100 * uf.n_C__C_unit.mean() / uf.n_C__anchor_a1.mean(), "100*mean n_C C_unit / mean n_C anchor", src)
put("a2b_pct_nT_unit_of_anchor", 100 * uf.n_T__C_unit.mean() / uf.n_T__anchor_a1.mean(), "100*mean n_T C_unit / mean n_T anchor", src)
for (t, ls), g in uf.groupby(["task", "label_set"]):
    gm = m[(m.task == t) & (m.label_set == ls)]
    k = f"{t}_{ls}"
    put(f"a2b_{k}_n_folds", g.fold.nunique(), "distinct folds", src)
    put(f"a2b_{k}_cov_C_unit", g.coverage__C_unit.mean(), "mean over fold rows, 3 encoders", src)
    put(f"a2b_{k}_cov_C_block", g.coverage__C_block.mean(), "mean over fold rows, 3 encoders", src)
    put(f"a2b_{k}_diff", (g.coverage__C_unit - g.coverage__C_block).mean(), "mean C_unit - C_block", src)
    put(f"a2b_{k}_block_minus_a1", (gm.coverage__C_block - gm.coverage).mean(), "mean C_block - A1", src)

# ---------------------------------------------------------------- A2c, K and the share
k = pd.read_csv(A2 / "a2_coverage_vs_K.csv")
src = "A2_conditional/a2_coverage_vs_K.csv"
put("a2c_n_folds", len(k), "rows", src)
put("a2c_spearman_shortfall_share", spearmanr(k.shortfall, k.between_share)[0], "Spearman over folds", src)
put("a2c_spearman_shortfall_K", spearmanr(k.shortfall, k.K)[0], "Spearman over folds", src)
put("a2c_n_unit_folds", int((~k.block_fold).sum()), "block_fold False", src)
put("a2c_n_block_folds", int(k.block_fold.sum()), "block_fold True", src)
put("a2c_cov_unit_folds", k[~k.block_fold].coverage_observed.mean(), "mean", src)
put("a2c_cov_block_folds", k[k.block_fold].coverage_observed.mean(), "mean", src)
put("a2c_n_block_folds_COAD", int((k.block_fold & (k.task == "COAD")).sum()), "COAD block folds", src)
put("a2c_max_K_unit_folds", k[~k.block_fold].K.max(), "max K over unit-calibrated folds", src)
put("a2c_max_K_any_fold", k.K.max(), "max K over folds", src)
s = pd.read_csv(A2 / "a2_simulated_coverage.csv")
sf = s[s.scope == "fold"]
inside = (sf.coverage_observed >= sf.simulated_coverage_q05) & (sf.coverage_observed <= sf.simulated_coverage_q95)
bf = sf.block_fold.astype(bool)
src = "A2_conditional/a2_simulated_coverage.csv (scope=fold)"
put("a2c_pct_unit_inside_band", 100 * inside[~bf].mean(), "% unit folds inside simulated q05-q95", src)
put("a2c_n_block_inside_band", int(inside[bf].sum()), "block folds inside band", src)
put("a2c_sim_mean_min", sf.simulated_coverage_mean.min(), "min simulated mean", src)
put("a2c_sim_mean_max", sf.simulated_coverage_mean.max(), "max simulated mean", src)

# ---------------------------------------------------------------- A2a, PRAD share by fold
p = k[(k.task == "PRAD") & (k.design == "donor")]
src = "A2_conditional/a2_coverage_vs_K.csv (PRAD, donor)"
for f, g in p.groupby("fold"):
    put(f"a2a_prad_{f}_share_min", g.between_share.min(), "min over 3 encoders", src)
    put(f"a2a_prad_{f}_share_max", g.between_share.max(), "max over 3 encoders", src)

# ---------------------------------------------------------------- A2d, PRAD donor sharing
ps = pd.read_csv(A2 / "a2_prad_donor_sharing.csv", dtype={"level": str})
pair = ps[(ps.fragment == "paired") & (ps.level == "pair")]
src = "A2_conditional/a2_prad_donor_sharing.csv (fragment=paired, level=pair)"
for sc, g in pair.groupby("score"):
    x = g.coverage_diff_share_minus_noshare.astype(float)
    put(f"a2d_paired_{sc}_mean", x.mean(), "mean share - noshare", src)
    put(f"a2d_paired_{sc}_n", len(x), "pairs", src)
    put(f"a2d_paired_{sc}_n_positive", int((x > 0).sum()), "pairs > 0", src)
    put(f"a2d_paired_{sc}_n_test_slides", g.test_slide.nunique(), "distinct test slides", src)
put("a2d_paired_pct_res_shared_share", 100 * (pair.res_group_shared_share.astype(str) == "True").mean(), "% pairs whose share draw shares resolution group", src)
arm = ps[(ps.fragment == "arm") & (ps.level == "paired_by_slide")]
x = arm.same_donor_minus_other_donor.astype(float)
src = "A2_conditional/a2_prad_donor_sharing.csv (fragment=arm, level=paired_by_slide)"
put("a2d_arm_mean", x.mean(), "mean same-donor-allowed - other-donor", src)
put("a2d_arm_sd", x.std(), "sd", src)
put("a2d_arm_n", len(x), "slide-encoder pairs", src)
put("a2d_arm_n_test_slides", arm.test_slide.nunique(), "distinct test slides", src)
ab = ps[(ps.fragment == "arm") & (ps.level == "arm_by_slide")].copy()
ab["width_mean"] = ab.width_mean.astype(float)
w = ab.groupby("arm").width_mean.mean()
put("a2d_arm_pct_wider", 100 * (w["slide_out_cal_other_donor"] / w["slide_out"] - 1), "% other-donor width above slide_out", src)

# ---------------------------------------------------------------- A2e, width by encoder
we = pd.read_csv(A2 / "a2_width_by_encoder.csv")
src = "A2_conditional/a2_width_by_encoder.csv"
g = we.groupby("design").first()
put("a2e_spearman_width_mean_min", g.spearman_width_mean_vs_pearson.min(), "min over designs", src)
put("a2e_spearman_width_mean_max", g.spearman_width_mean_vs_pearson.max(), "max over designs", src)
put("a2e_cov_range_max", g.coverage_range_across_encoders.max(), "max over designs", src)
put("a2e_cov_range_min", g.coverage_range_across_encoders.min(), "min over designs", src)

# ---------------------------------------------------------------- A3, weighted and hierarchical
A3 = R / "A3_weighted"
bf = pd.read_csv(A3 / "a3_by_fold.csv", low_memory=False)
KEY = ["encoder", "task", "label_set", "design", "fold", "repeat", "cal_draw"]
sh = bf[bf.design != "random"]
a10 = np.isclose(sh.alpha, 0.10)
a20 = np.isclose(sh.alpha, 0.20)
base = sh[(sh.score == "abs") & a10]
src = "A3_weighted/a3_by_fold.csv (designs patient, donor, slide_out; score abs; alpha 0.10)"


def paired(w, subset="all"):
    """Weighting w against `none` on the same subset, same fold cell."""
    ww = base[(base.weighting == w) & (base.subset == subset)].set_index(KEY)
    nn = base[(base.weighting == "none") & (base.subset == subset)].set_index(KEY)
    ww = ww.assign(cov_none=nn.coverage.reindex(ww.index), width_none=nn.width_mean.reindex(ww.index))
    assert ww.cov_none.notna().all()
    return ww.reset_index()


# W1
w1 = paired("W1")
put("a3_n_cells_per_weighting", len(w1), "fold cells, 3 encoders", src)
put("a3_w1_auc_holdout_min", w1.auc_holdout.min(), "min held-out AUC", src)
put("a3_w1_pct_auc_ge_09", 100 * (w1.auc_holdout >= 0.9).mean(), "% cells held-out AUC >= 0.9", src)
put("a3_w1_neff_pct_median", 100 * w1.n_eff_frac.median(), "median n_eff / n_C, %", src)
put("a3_w1_pct_neff_lt_5", 100 * (w1.n_eff_frac < 0.05).mean(), "% cells n_eff/n_C < 5%", src)
put("a3_w1_neff_pct_max", 100 * w1.n_eff_frac.max(), "max n_eff / n_C, %", src)
d1 = w1.coverage - w1.cov_none
put("a3_w1_move_mean", d1.mean(), "mean W1 - none coverage", src)
put("a3_w1_move_sd", d1.std(), "sd", src)
put("a3_w1_spearman_move_neff", spearmanr(d1, w1.n_eff_frac)[0], "Spearman(move, n_eff/n_C)", src)
for (t, dsg), g in w1.groupby(["task", "design"]):
    if (t, dsg) in {("LYMPH_IDC", "donor"), ("LYMPH_IDC", "patient"), ("SKCM", "donor"), ("SKCM", "patient"),
                    ("HCC", "donor"), ("HCC", "patient"), ("LUNG", "donor"), ("LUNG", "patient"),
                    ("PRAD", "slide_out"), ("CCRCC", "donor")}:
        put(f"a3_w1_{t}_{dsg}_none", g.cov_none.mean(), "mean none coverage", src)
        put(f"a3_w1_{t}_{dsg}_w1", g.coverage.mean(), "mean W1 coverage", src)
        put(f"a3_w1_{t}_{dsg}_move", (g.coverage - g.cov_none).mean(), "mean W1 - none", src)
        put(f"a3_w1_{t}_{dsg}_width_none", g.width_none.mean(), "mean none width", src)
        put(f"a3_w1_{t}_{dsg}_width_w1", g.width_mean.mean(), "mean W1 width", src)
        put(f"a3_w1_{t}_{dsg}_neff_pct", 100 * g.n_eff_frac.median(), "median n_eff/n_C %", src)
# W1b, on the morphology-joined subset
w1b = paired("W1b", "morph_joined")
put("a3_w1b_neff_pct_median", 100 * w1b.n_eff_frac.median(), "median n_eff / n_C, %", src + ", subset morph_joined")
put("a3_w1b_pct_neff_ge_30", 100 * (w1b.n_eff_frac >= 0.30).mean(), "% cells n_eff/n_C >= 30%", src)
put("a3_w1b_auc_holdout_median", w1b.auc_holdout.median(), "median held-out AUC", src)
d1b = w1b.coverage - w1b.cov_none
put("a3_w1b_move_mean", d1b.mean(), "mean W1b - none (same subset)", src)
put("a3_w1b_move_median", d1b.median(), "median", src)
put("a3_w1b_pct_toward_nominal", 100 * ((w1b.coverage - 0.9).abs() < (w1b.cov_none - 0.9).abs()).mean(), "% cells closer to 0.90 than none", src)
put("a3_w1b_spearman_move_neff", spearmanr(d1b, w1b.n_eff_frac)[0], "Spearman(move, n_eff/n_C)", src)
put("a3_frac_morph_joined_median_pct", 100 * w1b.frac_morph_joined.median(), "median joined fraction, %", src)
put("a3_frac_morph_joined_min_pct", 100 * w1b.frac_morph_joined.min(), "min joined fraction, %", src)
for (t, dsg), g in w1b.groupby(["task", "design"]):
    if t in {"SKCM", "IDC", "CCRCC"} and dsg in {"donor", "patient"}:
        ls = g.label_set.iloc[0] if g.label_set.nunique() == 1 else "mixed"
        for lab, gg in g.groupby("label_set"):
            put(f"a3_w1b_{t}_{lab}_{dsg}_none", gg.cov_none.mean(), "mean none coverage (morph subset)", src)
            put(f"a3_w1b_{t}_{lab}_{dsg}_w1b", gg.coverage.mean(), "mean W1b coverage", src)
            put(f"a3_w1b_{t}_{lab}_{dsg}_width_none", gg.width_none.mean(), "mean none width", src)
            put(f"a3_w1b_{t}_{lab}_{dsg}_width_w1b", gg.width_mean.mean(), "mean W1b width", src)
            put(f"a3_w1b_{t}_{lab}_{dsg}_neff_pct", 100 * gg.n_eff_frac.median(), "median n_eff/n_C %", src)
# W2
w2 = paired("W2")
d2 = w2.coverage - w2.cov_none
put("a3_w2_move_mean", d2.mean(), "mean W2 - none", src)
put("a3_w2_move_median", d2.median(), "median", src)
put("a3_w2_spearman_move_neff", spearmanr(d2, w2.n_eff_frac)[0], "Spearman(move, n_eff/n_C)", src)
for (t, lab, dsg), g in w2.groupby(["task", "label_set", "design"]):
    t = t if t != "IDC" else f"IDC_{lab}"
    put(f"a3_w2_{t}_{dsg}_nosupport_n", int(g.no_support.sum()), "cells with no_support", src)
    put(f"a3_w2_{t}_{dsg}_cells", len(g), "cells", src)
    put(f"a3_w2_{t}_{dsg}_nosupport_pct", 100 * g.no_support.mean(), "% cells with no_support", src)
# W3
w3 = sh[(sh.weighting == "W3") & (sh.score == "abs") & (sh.w3_variant == "nominal")].copy()
src3 = "A3_weighted/a3_by_fold.csv (W3 nominal, score abs, designs patient, donor, slide_out)"
w3["inf"] = w3.n_infinite > 0
w3["pred"] = (w3.K + 1) < (1 / w3.alpha) - 1e-9
put("a3_w3_n_cells", len(w3), "cells over both alphas", src3)
put("a3_w3_n_predicate_mismatch", int((w3.inf != w3.pred).sum()), "infinite flag != (K+1 < 1/alpha)", src3)
f10 = w3[np.isclose(w3.alpha, 0.10) & ~w3.inf]
put("a3_w3_a010_n_finite", len(f10), "finite cells at alpha 0.10", src3)
put("a3_w3_a010_finite_K", f10.K.max(), "K of the finite cells", src3)
put("a3_w3_a010_finite_cov_mean", f10.coverage.mean(), "mean coverage of finite cells", src3)
put("a3_w3_a010_finite_cov_min", f10.coverage.min(), "min coverage of finite cells", src3)
for (t, dsg), g in w3[np.isclose(w3.alpha, 0.20) & ~w3.inf & (w3.calibration_unit != "block")].groupby(["task", "design"]):
    put(f"a3_w3_a020_{t}_{dsg}_K", g.K.median(), "median K", src3)
    put(f"a3_w3_a020_{t}_{dsg}_cov_mean", g.coverage.mean(), "mean coverage, finite, unit-calibrated", src3)
    put(f"a3_w3_a020_{t}_{dsg}_cov_min", g.coverage.min(), "min coverage", src3)
fin = w3[~w3.inf].copy()
nn_all = sh[(sh.weighting == "none") & (sh.subset == "all") & (sh.score == "abs")]
nn_all = nn_all.set_index(KEY + ["alpha"])
fin = fin.set_index(KEY + ["alpha"])
fin["cov_none"] = nn_all.coverage.reindex(fin.index)
fin["width_none"] = nn_all.width_mean.reindex(fin.index)
fin = fin.reset_index()
for blk, g in fin.groupby(fin.calibration_unit == "block"):
    lab = "block" if blk else "unit"
    put(f"a3_w3_finite_{lab}_n", len(g), "finite cells", src3)
    put(f"a3_w3_finite_{lab}_lift_mean", (g.coverage - g.cov_none).mean(), "mean W3 - none", src3)
    put(f"a3_w3_finite_{lab}_lift_sd", (g.coverage - g.cov_none).std(), "sd", src3)
    put(f"a3_w3_finite_{lab}_width_ratio", (g.width_mean / g.width_none).mean(), "mean per-cell width ratio", src3)
    g20 = g[np.isclose(g.alpha, 0.20)]
    put(f"a3_w3_finite_{lab}_a020_cov_mean", g20.coverage.mean(), "mean coverage at alpha 0.20", src3)
fb = sh[(sh.weighting == "W3") & (sh.score == "abs") & (sh.w3_variant == "feasible_level")]
srcf = "A3_weighted/a3_by_fold.csv (W3 feasible_level, abs; alpha is 1/(K+1) on these rows)"
put("a3_fallback_alpha_values", fb.alpha.nunique(), "distinct alpha on fallback rows", srcf)
put("a3_fallback_n", len(fb), "cells", srcf)
put("a3_fallback_cov_mean", fb.coverage.mean(), "mean realised coverage", srcf)
put("a3_fallback_guaranteed_mean", fb.guaranteed_level.mean(), "mean guaranteed level", srcf)
put("a3_fallback_pct_meets", 100 * (fb.coverage >= fb.guaranteed_level).mean(), "% realised >= guaranteed", srcf)
# scaled_clip against abs, unweighted
nb2 = sh[(sh.weighting == "none") & (sh.subset == "all") & a10].pivot_table(
    index=KEY, columns="score", values=["coverage", "width_mean", "width_median"])
srcs = "A3_weighted/a3_by_fold.csv (none, subset all, alpha 0.10, designs patient, donor, slide_out)"
put("a3_sc_n", len(nb2), "paired cells", srcs)
put("a3_sc_cov_abs", nb2[("coverage", "abs")].mean(), "mean", srcs)
put("a3_sc_cov_clip", nb2[("coverage", "scaled_clip")].mean(), "mean", srcs)
put("a3_sc_width_abs", nb2[("width_mean", "abs")].mean(), "mean of mean width", srcs)
put("a3_sc_width_clip", nb2[("width_mean", "scaled_clip")].mean(), "mean of mean width", srcs)
put("a3_sc_width_ratio_of_means", nb2[("width_mean", "scaled_clip")].mean() / nb2[("width_mean", "abs")].mean(), "ratio of means", srcs)
put("a3_sc_width_ratio_median", (nb2[("width_mean", "scaled_clip")] / nb2[("width_mean", "abs")]).median(), "median per-cell ratio", srcs)
put("a3_sc_width_ratio_mean", (nb2[("width_mean", "scaled_clip")] / nb2[("width_mean", "abs")]).mean(), "mean per-cell ratio", srcs)
put("a3_sc_medwidth_abs", nb2[("width_median", "abs")].mean(), "mean of median width", srcs)
put("a3_sc_medwidth_clip", nb2[("width_median", "scaled_clip")].mean(), "mean of median width", srcs)
scc = sh[(sh.weighting == "none") & (sh.subset == "all") & a10 & (sh.score == "scaled_clip")]
put("a3_sc_pct_floor_binds", 100 * scc.sigma_lo_hit_guard.astype(bool).mean(), "% cells where the lower clip hits the 1e-3 floor", srcs)
# none against A1's committed by_fold, both invocations, fold level (mean over repeats and draws)
nn_f = bf[(bf.weighting == "none") & (bf.subset == "all") & (bf.score == "abs") & np.isclose(bf.alpha, 0.10)]
nn_f = nn_f.groupby(["encoder", "task", "label_set", "design", "fold"]).coverage.mean().reset_index()
a1b = pd.concat([pd.read_csv(A1 / f"a1_by_fold__{e}__{t}.csv").assign(encoder=e) for e in ENC3 for t in ["main", "slideout"]])
a1b = a1b[a1b.score == "abs"].copy()
nn_f["fold"] = nn_f.fold.astype(str)
a1b["fold"] = a1b.fold.astype(str)
mf = nn_f.merge(a1b[["encoder", "task", "label_set", "design", "fold", "coverage"]],
                on=["encoder", "task", "label_set", "design", "fold"], suffixes=("", "_a1"), validate="one_to_one")
assert len(mf) == len(nn_f)
put("a3_none_vs_a1_n_fold_rows", len(mf), "fold rows matched to A1 by_fold", "A3_weighted/a3_by_fold.csv; A1_coverage/a1_by_fold__<enc>__<tag>.csv")
put("a3_none_vs_a1_max_abs", float((mf.coverage - mf.coverage_a1).abs().max()), "max |none - A1|", "same")
# IDC audited with and without
nn10 = base[(base.weighting == "none") & (base.subset == "all")]
put("a3_none_cov_all", nn10.coverage.mean(), "mean none coverage, all cells", src)
put("a3_none_cells_all", len(nn10), "cells", src)
put("a3_none_cov_excl_idc_audited", nn10[nn10.label_set != "audited"].coverage.mean(), "excluding IDC audited", src)
put("a3_none_cells_excl_idc_audited", int((nn10.label_set != "audited").sum()), "cells", src)

out = pd.DataFrame(rows)
out.to_csv(R / "A3_report_numbers.csv", index=False, float_format="%.10g")
print(f"wrote {R / 'A3_report_numbers.csv'} ({len(out)} rows)")
