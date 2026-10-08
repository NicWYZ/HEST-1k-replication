"""Round 5 PPI, stage E0 item 2 and the brief-claims extraction.

Run on a Longleaf compute node, from its own output directory, after the code clone exists.
Writes
  e0_setup_checks.csv     one row per check with expected, observed and pass
  e0_parquet_md5.csv      every prediction parquet of brief section 3 with its md5
  e0_round4_stamps.csv    ownership stamps found under results/round4 of the project tree
  e0_brief_claims.csv     the cells of the committed round-4 tables that the brief quotes,
                          extracted without interpretation, for the lead to compare with the text
"""
import argparse
import json
import os
import subprocess

import numpy as np
import pandas as pd

import round5_ppi_common as C

EXPECTED_MD5 = {
    "code/scripts/round4_ppi_estimator.py": "d79e69aa65800b9d24de556e019a0c64",
    "code/scripts/round4_ppi_q2_masking.py": "15f51917a5fb79702ba239e520e7ff86",
    "code/scripts/round4_ppi_q3_regimes.py": "6097231bc238c0a23387ce76029acefd",
    "code/scripts/round3_a0_harness.py": "0ad7ae8efe554c1f285e5f384a9fb7f5",
}


def git(path, *args):
    r = subprocess.run(["git", "--no-optional-locks", "-C", path, *args], capture_output=True, text=True)
    return r.stdout.strip() or r.stderr.strip()


def setup_checks(frame_id):
    rows = []
    for rel, exp in EXPECTED_MD5.items():
        obs = C.md5(os.path.join(C.CLONE, rel))
        rows.append(("clone_md5", rel, exp, obs, obs == exp))
    rows.append(("clone_head", C.CLONE, "", git(C.CLONE, "rev-parse", "HEAD"), True))
    rows.append(("clone_branch", C.CLONE, "round5-ppi", git(C.CLONE, "rev-parse", "--abbrev-ref", "HEAD"),
                 git(C.CLONE, "rev-parse", "--abbrev-ref", "HEAD") == "round5-ppi"))
    head = git(C.ROOT, "rev-parse", "HEAD")
    rows.append(("project_tree_head", C.ROOT, "9d7277d", head, head.startswith("9d7277d")))
    rows.append(("project_tree_branch", C.ROOT, "main", git(C.ROOT, "rev-parse", "--abbrev-ref", "HEAD"),
                 git(C.ROOT, "rev-parse", "--abbrev-ref", "HEAD") == "main"))
    w = C.whose(os.path.join(C.ROOT, "results/round4"), frame_id)
    rows.append(("whose_results_round4", "results/round4", "", w["verdict"] + ("" if w["stamp"] is None else " " + json.dumps(w["stamp"])), True))
    return rows


def parquet_checks():
    rec = json.load(open(os.path.join(C.CLONE, "results/round4/ppi/Q5_joint/cluster_unit/q5_input_md5.json")))
    rec = {k.replace(C.ROOT + "/", ""): v for k, v in rec.items()}
    rows = []
    for (vtag, arm), rel in list(C.TISSUE_PARQUETS.items()) + list(C.ACS_PARQUETS.items()):
        p = os.path.join(C.ROOT, rel)
        ex = os.path.exists(p)
        obs = C.md5(p) if ex else ""
        exp = rec.get(rel, "")
        rows.append(dict(vtag=vtag, arm=arm, path=rel, exists=ex, size_bytes=os.path.getsize(p) if ex else -1,
                         md5=obs, recorded_md5=exp, md5_match=(obs == exp) if exp else None))
    return pd.DataFrame(rows)


def brief_claims():
    R = lambda rel: pd.read_csv(os.path.join(C.CLONE, rel), low_memory=False)
    out = []

    def add(claim, source, filt, val, note=""):
        out.append(dict(claim=claim, source=source, filter=filt, value=val, note=note))

    # 2.4 bullets 1 and 2, within-cluster R2 on the z scale
    src = "results/round4/ppi/Q2_theory/q2_cluster_r2.csv"
    r2 = R(src)
    r2 = r2[(r2.scale == "z") & (r2.population == "donor")]
    for (vt, arm, est), g in r2.groupby(["vtag", "arm", "estimand"]):
        add("R2_within_median_over_genes", src, f"{vt}|{arm}|{est}|donor|z", float(np.nanmedian(g.R2_within)), f"n_genes={len(g)}")
        add("R2_cluster_raw_median_over_genes", src, f"{vt}|{arm}|{est}|donor|z", float(np.nanmedian(g.R2_cluster_raw)), f"n_genes={len(g)}")
    # 2.4 bullet 3 and 2.1, regime B rows of the main table
    src = "results/round4/ppi/Q4_tables/q4_main_table.csv"
    mt = R(src)
    b = mt[mt.regime == "B"]
    for keys, g in b.groupby(["vtag", "arm", "estimand", "population", "target", "lambda_rule", "cost"], dropna=False):
        add("regB_width_ratio_range", src, "|".join(map(str, keys)),
            f"{g.width_ratio_median.min():.6g}..{g.width_ratio_median.max():.6g}", f"rows={len(g)} m={sorted(set(g.m.astype(str)))}")
        add("regB_coverage_range", src, "|".join(map(str, keys)),
            f"{g.coverage_median.min():.6g}..{g.coverage_median.max():.6g}", f"rows={len(g)}")
    # 2.4 bullet 4, fitted m* at cost ratio 100
    src = "results/round4/ppi/Q2_theory/q2_report_numbers.csv"
    rn = R(src)
    sel = rn[rn.name.str.contains(r"\|theta3\|donor\|") & rn.name.str.endswith("m_star_cd_cs_100_median")]
    for _, r in sel.iterrows():
        add("m_star_cd_cs_100", src, r["name"], r["value"])
    # 2.1 and E1, q4a table 6.1, theta3 donor design
    src = "results/round4/ppi/Q4a_recompute/q4a_table61.csv"
    t = R(src)
    t = t[(t.estimand == "theta3") & (t.population == "donor") & (t.target == "design")]
    for keys, g in t.groupby(["vtag", "arm", "interval", "lambda_rule"]):
        g6 = g[g.n_L >= 6]
        g8 = g[g.n_L >= 8]
        add("q4a_cov_nL_ge6", src, "|".join(map(str, keys)),
            f"{g6.coverage_median.min():.6g}..{g6.coverage_median.max():.6g}" if len(g6) else "")
        add("q4a_estvar_nL_ge8", src, "|".join(map(str, keys)),
            f"{g8.est_var_over_emp_var_median.min():.6g}..{g8.est_var_over_emp_var_median.max():.6g}" if len(g8) else "")
        add("q4a_empvar_ratio_nL8", src, "|".join(map(str, keys)),
            ";".join(f"{v:.6g}" for v in g[g.n_L == 8].emp_var_ratio_median))
    # E1 acceptance 4 source
    src = "results/round4/ppi/Q1_estimator/q1_coverage_by_G.csv"
    q1 = R(src)
    q1 = q1[(q1.target == "design") & (q1.form == "textbook") & (q1.lambda_rule == "none")]
    for _, r in q1.iterrows():
        add("q1_cov_median", src, f"{r.estimator}|{r.interval}|fpc={r.fpc}|G_L={r.G_L}", r.cov_median, f"n_cells={r.n_cells}")
    # 2.1 item 4
    src = "results/round4/ppi/Q4_tables/q4_report_numbers.csv"
    q4 = R(src)
    for _, r in q4[q4.name.str.contains("narrow|B_wins|regB|regime", case=False)].iterrows():
        add("q4_report_number", src, r["name"], r["value"])
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    a = ap.parse_args()
    out = os.getcwd()
    rows = setup_checks(a.frame_id)
    pq = parquet_checks()
    for _, r in pq.iterrows():
        rows.append(("parquet_exists", r.path, True, r.exists, bool(r.exists)))
        if r.recorded_md5:
            rows.append(("parquet_md5", r.path, r.recorded_md5, r.md5, bool(r.md5_match)))
    pd.DataFrame(rows, columns=["check", "item", "expected", "observed", "pass"]).to_csv("e0_setup_checks.csv", index=False)
    pq.to_csv("e0_parquet_md5.csv", index=False)
    pd.DataFrame(C.scan_tree(os.path.join(C.ROOT, "results/round4"), max_depth=4)).to_csv("e0_round4_stamps.csv", index=False)
    brief_claims().to_csv("e0_brief_claims.csv", index=False)
    print("checks", len(rows), "failed", sum(1 for r in rows if not r[4]))


if __name__ == "__main__":
    main()
