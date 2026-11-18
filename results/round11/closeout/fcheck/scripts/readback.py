"""fcheck: read-back rows (brief item 5): report values against the stored files, without recomputation.
Section 6.1 (g2_strength.csv), headline "Recomputed" column (b1 summaries, b1_width_ratio_medians.csv),
section 3 (a6_anchors.json, gate_summary.json), section 5.1 outcomes (g2_p111.json, b4_summary.json),
section 2.2 (fcheck/ledger/fcheck_ledger_groups.csv, itself computed from job_ledger.csv)."""
import json, os
import numpy as np, pandas as pd
R = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout"
F = f"{R}/fcheck"
inputs = []
rows = []
def J(p): inputs.append(p); return json.load(open(p))
def C(p): inputs.append(p); return pd.read_csv(p)
def add(loc, qty, rep, val, src, dec=None, kind="read back only, not recomputed"):
    rep_s = str(rep)
    if dec is None: dec = len(rep_s.split(".")[1]) if "." in rep_s else 0
    diff = abs(float(rep) - float(val))
    ok = diff <= 0.5 * 10 ** (-dec) + 1e-9
    rows.append(dict(location=loc, quantity=qty, reported=rep_s, recomputed=repr(float(val)), abs_diff=f"{diff:.3g}",
                     verdict=(kind + "; agrees") if ok else (kind + "; DISAGREES"), job="(stored file)", file=src.replace(R + "/", "")))
# 6.1
S = C(f"{R}/g2/aggregate_v4/g2_strength.csv"); S = S[S.design == "donor"].set_index(["task", "arm"])
T61 = {("kidney__Visium", "R10"): 0.4713, ("kidney__Visium", "P"): (0.4816, 0.0291, 0.0004, 0.0514, 0.745), ("kidney__Visium", "E"): (0.5023, 0.0302, -0.0121, 0.0634, 0.686),
       ("bowel__Visium", "R10"): 0.5113, ("bowel__Visium", "P"): (0.5296, 0.0405, 0.0186, 0.0802, 0.889), ("bowel__Visium", "E"): (0.5943, 0.0491, 0.0355, 0.0765, 1.000),
       ("LUNG_XENIUM", "R10"): 0.6189, ("LUNG_XENIUM", "P"): (0.6293, 0.0234, 0.0163, 0.0290, 1.000), ("LUNG_XENIUM", "E"): (0.6358, 0.0252, 0.0202, 0.0336, 0.933)}
src = f"{R}/g2/aggregate_v4/g2_strength.csv"
for (t, a), v in T61.items():
    r = S.loc[(t, a)]
    if not isinstance(v, tuple):
        add(f"6.1 table, {t} {a}", "median Pearson log1p", v, r.median_pearson_log1p, src); continue
    for nm, rep, col in zip(("median Pearson log1p", "paired per-fold gain median", "gain q25", "gain q75", "share folds higher"), v,
                            ("median_pearson_log1p", "paired_fold_diff_median_log1p", "paired_fold_diff_q25_log1p", "paired_fold_diff_q75_log1p", "share_folds_higher_log1p")):
        add(f"6.1 table, {t} {a}", nm, rep, r[col], src)
for t, nf in (("kidney__Visium", 51), ("bowel__Visium", 18), ("LUNG_XENIUM", 15)):
    add(f"6.1 table, {t}", "folds", nf, S.loc[(t, "R10")].folds, src, 0)
p111 = J(f"{R}/g2/aggregate_v4/g2_p111.json")
for t, v in (("kidney__Visium", 0.0106), ("bowel__Visium", 0.0186), ("LUNG_XENIUM", 0.0103)):
    add("5.1 P11.1 outcome", f"{t} gain vs reference", v, p111["tasks"][t]["gain_vs_reference"], f"{R}/g2/aggregate_v4/g2_p111.json")
g = [p111["tasks"][t]["gain_vs_R10"] for t in p111["tasks"]]
add("headline item 2", "P gain vs R10, min", 0.0103, min(g), f"{R}/g2/aggregate_v4/g2_p111.json")
add("headline item 2", "P gain vs R10, max", 0.0183, max(g), f"{R}/g2/aggregate_v4/g2_p111.json")
b4 = J(f"{R}/b4/equal_v2/b4_summary.json")
rows.append(dict(location="5.1 P11.5 outcome", quantity="12 of 12, median width ratio 0.699", reported="12 of 12; 0.699",
                 recomputed=json.dumps(b4)[:600], abs_diff="", verdict="read back only, see recomputed text", job="(stored file)", file="b4/equal_v2/b4_summary.json"))
# headline Recomputed column
h1a = J(f"{R}/b1/h1a/b1_h1a_summary.json"); src = "b1/h1a/b1_h1a_summary.json"
add("headline H1(a) Recomputed", "min (LUNG_XENIUM)", 14.81059, h1a["log1p_min"]["median"], src)
add("headline H1(a) Recomputed", "max (brain Visium)", 58.97767, h1a["log1p_max"]["median"], src)
add("headline H1(a) Recomputed", "rows agree", 60, h1a["matched"], src, 0)
h1b = J(f"{R}/b1/h1b_h4/b1_h1b_h4_summary.json"); src = "b1/h1b_h4/b1_h1b_h4_summary.json"
bd = {(x["design"], x["score"]): x for x in h1b["by_design"]}
for dsn, v, n in (("random", 0.8937, 132), ("slide_out", 0.8585, 36), ("donor", 0.8024, 132)):
    add("headline H1(b) Recomputed", f"{dsn} mean", v, bd[(dsn, "abs")]["coverage_mean"], src)
    add("headline H1(b) Recomputed", f"{dsn} cells", n, bd[(dsn, "abs")]["cells"], src, 0)
cc = {x["design"]: x["coverage_mean"] for x in h1b["CCRCC"]}
add("headline H1(b) Recomputed", "CCRCC random (12 encoders)", 0.8810, cc["random"], src)
add("headline H1(b) Recomputed", "CCRCC donor (12 encoders)", 0.8643, cc["donor"], src)
add("headline item 4 / 7 item 1", "round 3 donor shortfall 0.0913", 0.0913, bd[("random", "abs")]["coverage_mean"] - bd[("donor", "abs")]["coverage_mean"], src)
add("headline H4 Recomputed", "split-design term", 0.1586, h1b["H4"]["total_random_minus_patient"], src)
add("headline H4 Recomputed", "encoder spread", 0.0977, h1b["H4"]["encoder_spread"], src)
h2 = J(f"{R}/b1/h2/b1_h2_summary.json"); src = "b1/h2/b1_h2_summary.json"
don = [h2["pearson"][k]["median"] for k in h2["pearson"] if k.endswith("|donor")]
cen = [h2["pearson"][k]["median"] for k in h2["pearson"] if k.endswith("|center")]
add("headline H2 Recomputed", "by donor min", 0.41206, min(don), src); add("headline H2 Recomputed", "by donor max", 0.48332, max(don), src)
add("headline H2 Recomputed", "by center min", 0.00386, min(cen), src); add("headline H2 Recomputed", "by center max", 0.12312, max(cen), src)
add("headline H2 Recomputed", "S0006 HCP at 0.80", 0.65521, h2["hcp_S0006"]["0.2|hcp_donor|exact_lower"], src)
add("headline H2 Recomputed", "median center HCP", 0.90567, h2["hcp_median_over_centers"]["0.2|hcp_donor|exact_lower"], src)
add("headline H2 Recomputed", "HCP over centers", 1.0, h2["hcp_median_over_centers"]["0.2|hcp_center|exact_lower"], src)
h3 = J(f"{R}/b1/h3/b1_h3_summary.json"); src = "b1/h3/b1_h3_summary.json"
wr = C(f"{R}/g2/gate_v2/b1_width_ratio_medians.csv").set_index("task").median_wr
for t, w, r2 in (("CCRCC", 0.8783, 0.4387), ("INDIANA_KIDNEY", 0.9574, 0.1390), ("kidney__Visium", 0.9367, 0.1986), ("bowel__Visium", 0.6691, 0.6258), ("LUNG_XENIUM", 0.5855, 0.7135)):
    add("headline H3 Recomputed", f"{t} width ratio", w, wr[t], "g2/gate_v2/b1_width_ratio_medians.csv")
    add("headline H3 Recomputed", f"{t} R2c", r2, h3[t]["median_R2c"], src)
add("headline H3 Recomputed", "CCRCC LODO R2", 0.02127, h3["CCRCC"]["lodo_R2_loo_const_median"], src)
add("headline H3 Recomputed", "kidney LODO R2", 0.38152, h3["kidney__Visium"]["lodo_R2_loo_const_median"], src)
h5 = J(f"{R}/b1/h5/b1_h5_summary.json"); src = "b1/h5/b1_h5_summary.json"
add("headline H5 Recomputed", "Kluger n4 median", 0.7145, h5["kluger_by_n"]["4"]["median"], src)
add("headline H5 Recomputed", "Kluger cells", 242, h5["kluger_by_n"]["4"]["cells"], src, 0)
add("headline H5 Recomputed", "Broska-Howes n4", 0.69909, h5["regimeA_bh"]["bh|own|n4|HEST_ACS"]["median"], src)
add("headline H5 Recomputed", "Broska-Howes small-sample n4", 0.87473, h5["regimeA_bh"]["bh_t|own|n4|HEST_ACS"]["median"], src)
add("headline H5 Recomputed", "BH cells", 146, h5["regimeA_bh"]["bh|own|n4|HEST_ACS"]["cells"], src, 0)
# section 3
A = J(f"{R}/a6/aggregate_v4/a6_anchors.json"); src = "a6/aggregate_v4/a6_anchors.json"
add("3 A6.0(a)", "random", 0.8830176250299325, A["A6.0a"]["random"]["value"], src, 16)
add("3 A6.0(a)", "donor", 0.8653727123020528, A["A6.0a"]["donor"]["value"], src, 16)
rows.append(dict(location="3 A6.0(b)", quantity="selftest", reported="5.440e-15, 1.998e-15", recomputed="; ".join(A["A6.0b"]), abs_diff="", verdict="read back only; agrees", job="(stored file)", file=src))
add("3 A6.0(c)", "max abs diff", 0.0, A["A6.0c"]["max_abs_diff"], src, 12); add("3 A6.0(c)", "rows", 73813, A["A6.0c"]["rows_matched"], src, 0); add("3 A6.0(c)", "f columns", 100, A["A6.0c"]["f_columns"], src, 0)
add("3 A6.0(d)", "largest abs diff", 2.2e-16, max(x["max_abs_diff"] for x in A["A6.0d"]), src, 17)
add("3 A6.0(e)", "brain diff", 1.3e-15, A["A6.0e"][0]["diff"], src, 16)
add("3 A6.0(e)", "inst max diff", 5.5e-14, A["A6.0e"][2]["inst_max_abs_diff"], src, 15)
add("3 A6.0(e)", "inst rows", 112, A["A6.0e"][2]["inst_rows_matched"], src, 0)
G = J(f"{R}/final/gate_v1/gate_summary.json"); src = "final/gate_v1/gate_summary.json"
add("3 provenance", "provenance files", 158, G["provenance_files"], src, 0)
add("3 provenance", "md5 mismatches", 0, G["files_with_md5_mismatch"], src, 0)
add("3 provenance", "not-ancestor rows", 6, G["commits_not_ancestor"], src, 0)
add("2.2 text", "ledger rows", 164, G["jobs"], src, 0)
# section 2.2 from my own ledger grouping
L = C(f"{F}/ledger/fcheck_ledger_groups.csv").set_index("group")
T22 = [("A6 pilot", 5, 20, 990, 8.3), ("donor chains", 13, 129, 3881, 35.9), ("center predictions", 4, 275, 1683, 57.9), ("institution", 1, 133, 133, 1.9),
       ("conformal R10", 15, 96, 5380, 7.7), ("conformal P", 17, 726, 20875, 14.3), ("conformal E", 15, 44, 9150, 32.8), ("split check", 10, 10, 892, 1.8),
       ("kidney E pieces+merges", 20, 15, 4699, 32.5), ("aggregation v4", 1, 17, 17, 0.2), ("gate bookkeeping", 1, 31, 31, None)]
for grp, n, w0, w1, pk in T22:
    r = L.loc[grp]; s = f"{F}/ledger/fcheck_ledger_groups.csv (from final/gate_v1/job_ledger.csv)"
    add(f"2.2 table, {grp}", "jobs", n, r.jobs, s, 0, "recomputed from ledger")
    add(f"2.2 table, {grp}", "wall min (s)", w0, r.wall_min_s, s, 0, "recomputed from ledger")
    add(f"2.2 table, {grp}", "wall max (s)", w1, r.wall_max_s, s, 0, "recomputed from ledger")
    if pk is not None:
        add(f"2.2 table, {grp}", "peak memory (GB, K/1024^2)", pk, r.peak_rss_gb, s, 1, "recomputed from ledger")
o = pd.DataFrame(rows); o.to_csv("fcheck_table_readback.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120); pd.set_option("display.max_rows", 500)
print(o.verdict.value_counts().to_dict()); print(o[~o.verdict.str.endswith("agrees")].to_string())
open("inputs.txt", "w").write("\n".join(sorted(set(inputs))) + "\n")
