#!/usr/bin/env python
"""Round 4 PPI, interval 2: markdown tables for docs/round4_ppi_Q3_report.md, read from the merged files.

Writes one markdown fragment per table into --res/Q3_regimes/report_tables/ and, with --report,
replaces each line '<!-- TABLE:<name> -->' ... '<!-- /TABLE -->' block in the report with the fragment.
Every value printed is copied from the CSV named in the fragment's caption line.
"""
import argparse
import os
import re

import numpy as np
import pandas as pd

TASKS = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA"]
HEST_ARMS = ["hoptimus0", "uni_v2", "resnet50", "permuted"]
ACS_ARMS = ["package", "permuted"]


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n.d."
    return f"{x:.{d}f}"


def md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--res", required=True)
    p.add_argument("--report")
    p.add_argument("--repo")
    a = p.parse_args()
    q2 = pd.read_csv(f"{a.res}/Q2_theory/q2_report_numbers.csv"); N2 = dict(zip(q2.name, q2.value))
    q3 = pd.read_csv(f"{a.res}/Q3_regimes/q3_report_numbers.csv"); N3 = dict(zip(q3.name, q3.value))
    r2 = pd.read_csv(f"{a.res}/Q2_theory/q2_cluster_r2.csv", low_memory=False)
    ry = r2[r2.scale == "log1p_y"].groupby(["vtag", "arm"])[["R2_unit", "R2_cluster_raw"]].median()
    tasks = [t for t in TASKS if f"Q2|{t}|permuted|nL_max" in N2]
    T = {}
    rows = []
    for t in tasks:
        for arm in (ACS_ARMS if t.startswith("ACS") else HEST_ARMS):
            tg = f"{t}|{arm}|theta3"
            rows.append({
                "task": t, "predictor": arm, "$n_L$": int(N2[f"Q2|{t}|{arm}|nL_max"]),
                "unit $R^2$ (outcome)": f(ry.R2_unit.get((t, arm), np.nan)),
                "cluster $R^2$ (outcome)": f(ry.R2_cluster_raw.get((t, arm), np.nan)),
                "$1-R^2_{\\text{cl}}$ (donor $z$)": f(N2.get(f"Q2.1|{tg}|donor|one_minus_R2_cluster_raw")),
                "ratio, donor, (c)": f(N2.get(f"Q2.1|{tg}|donor|super|c_crossfit|var_ratio_mall_nLmax")),
                "ratio, donor, (d1)": f(N2.get(f"Q2.1|{tg}|donor|super|d1_pretest|var_ratio_mall_nLmax")),
                "ratio, donor, (d2)": f(N2.get(f"Q2.1|{tg}|donor|super|d2_pretest|var_ratio_mall_nLmax")),
                "ratio, spot, (c)": f(N2.get(f"Q2.1|{tg}|spot|super|c_crossfit|var_ratio_mall_nLmax")),
            })
    T["q2_gain"] = ("Source `results/round4/ppi/Q2_theory/q2_report_numbers.csv` (names `Q2.1|...`) and "
                    "`q2_cluster_r2.csv` (scale `log1p_y`, median over genes); $\\theta_3$, $m$ = all, largest "
                    "$n_L$, superpopulation target, CR1.", pd.DataFrame(rows))
    rows = []
    for t in tasks:
        arm = "package" if t.startswith("ACS") else "hoptimus0"
        tg = f"{t}|{arm}|theta3|donor|super"
        rows.append({"task": t, "predictor": arm,
                     "classical, $m=200$": f(N2.get(f"Q2.2|{tg}|none|emp_var_m200_over_mall")),
                     "classical, $m=500$": f(N2.get(f"Q2.2|{tg}|none|emp_var_m500_over_mall")),
                     "(c), $m=200$": f(N2.get(f"Q2.2|{tg}|c_crossfit|emp_var_m200_over_mall")),
                     "(c), $m=500$": f(N2.get(f"Q2.2|{tg}|c_crossfit|emp_var_m500_over_mall")),
                     "$m^\\star$ classical": f(N2.get(f"Q2.3|{t}|{arm}|theta3|donor|none|m_star_cd_cs_100_median"), 0),
                     "$m^\\star_{\\text{PP}}$ (c)": f(N2.get(f"Q2.3|{t}|{arm}|theta3|donor|c_crossfit|m_star_cd_cs_100_median"), 0),
                     "$\\rho_r$ (c)": f(N2.get(f"Q2.3|{t}|{arm}|theta3|donor|c_crossfit|rho_r_median")),
                     "$m$ at $f=0.1$": f(N2.get(f"Q2.3|{t}|{arm}|theta3|donor|c_crossfit|m_at_f0.1_median"), 0)})
    T["q2_m"] = ("Source `results/round4/ppi/Q2_theory/q2_report_numbers.csv` (names `Q2.2|...`, `Q2.3|...`); "
                 "$\\theta_3$ donor-weighted, superpopulation target, variance at $m$ over variance at $m$ = all "
                 "at the largest $n_L$; $m^\\star$ at $c_d/c_s = 100$, median over genes.", pd.DataFrame(rows))
    rows = []
    for t in tasks:
        if t.startswith("ACS"):
            continue
        rows.append({"task": t, **{f"$m^\\star_{{\\text{{PP}}}}$ {e}": f(N2.get(f"Q2.3|{t}|{e}|theta3|donor|c_crossfit|m_star_cd_cs_100_median"), 1)
                                    for e in HEST_ARMS}})
    T["q2_mstar_enc"] = ("Source `results/round4/ppi/Q2_theory/q2_report_numbers.csv` (names "
                         "`Q2.3|<task>|<encoder>|theta3|donor|c_crossfit|m_star_cd_cs_100_median`).", pd.DataFrame(rows))
    q3tasks = sorted({n.split("|")[1] for n in q3.name if n.startswith("Q3.2|")}, key=lambda x: TASKS.index(x))
    rows = []
    for t in q3tasks:
        arm = "package" if t.startswith("ACS") else "hoptimus0"
        for B in (2400, 4800, 9600):
            r = {"task": t, "$B$": B,
                 "$m_B$": f(N3.get(f"Q3.2|{t}|{arm}|theta3|donor|c_crossfit|design|regB|B{B}|m_median"), 0)}
            for n in (4, 6, 8, 12):
                r[f"$n_L={n}$"] = f(N3.get(f"Q3.1|{t}|{arm}|theta3|donor|c_crossfit|super|B{B}|nL{n}|width_ratio_B_over_A"))
            r["classical, $n_L=8$"] = f(N3.get(f"Q3.1|{t}|{arm}|theta3|donor|none|super|B{B}|nL8|width_ratio_B_over_A"))
            for n in (4, 8):
                r[f"cost 100, $n_L={n}$"] = f(N3.get(f"Q3.1|{t}|{arm}|theta3|donor|c_crossfit|super|cost100|B{B}|nL{n}|width_ratio_B_over_A"))
            rows.append(r)
    T["q3_width"] = ("Source `results/round4/ppi/Q3_regimes/q3_report_numbers.csv` (names `Q3.1|...`); width ratio "
                     "regime B over regime A, $\\theta_3$ donor-weighted, rule (c) unless marked, superpopulation "
                     "target, unit cost unless marked; n.d. where regime B's cost-matched budget is below zero.",
                     pd.DataFrame(rows))
    rows = []
    for t in q3tasks:
        arm = "package" if t.startswith("ACS") else "hoptimus0"
        for B in (2400, 4800, 9600):
            r = {"task": t, "$B$": B}
            for rule in ("none", "c_crossfit"):
                r[f"design, {'classical' if rule == 'none' else '(c)'}"] = f(N3.get(f"Q3.2|{t}|{arm}|theta3|donor|{rule}|design|regB|B{B}|coverage_median"))
                r[f"cluster-robust, {'classical' if rule == 'none' else '(c)'}"] = f(N3.get(f"Q3.2|{t}|{arm}|theta3|donor|{rule}|super|regB|B{B}|coverage_median"))
            rows.append(r)
    T["q3_cov"] = ("Source `results/round4/ppi/Q3_regimes/q3_report_numbers.csv` (names `Q3.2|...|regB|...`); "
                   "regime B coverage of $\\theta_{\\text{full}}$, median over genes, $\\theta_3$ donor-weighted.",
                   pd.DataFrame(rows))
    sc = pd.read_csv(f"{a.res}/Q3_regimes/q3_prediction_scores.csv")
    s = sc[sc.scope == "SUMMARY"][["prediction", "value"]].rename(columns={"value": "criteria met / scored"})
    T["scores"] = ("Source `results/round4/ppi/Q3_regimes/q3_prediction_scores.csv` (rows with scope SUMMARY).", s)
    if a.repo:
        import glob
        import hashlib
        rows = []
        for fp in sorted(glob.glob(f"{a.repo}/code/scripts/round4_ppi_*.py") + glob.glob(f"{a.repo}/code/scripts/round4_ppi_*.sh")):
            rows.append({"script": f"`code/scripts/{os.path.basename(fp)}`",
                         "md5": f"`{hashlib.md5(open(fp, 'rb').read()).hexdigest()}`"})
        T["scripts"] = ("Scripts, with the md5 of the committed file (computed from the working tree at commit time).",
                        pd.DataFrame(rows))
    od = f"{a.res}/Q3_regimes/report_tables"; os.makedirs(od, exist_ok=True)
    frags = {}
    for k, (cap, df) in T.items():
        frag = md(df) + "\n\n" + cap
        frags[k] = frag
        open(f"{od}/{k}.md", "w").write(frag + "\n")
    if a.report:
        txt = open(a.report).read()
        for k, frag in frags.items():
            txt = re.sub(rf"<!-- TABLE:{k} -->.*?<!-- /TABLE -->", lambda m: f"<!-- TABLE:{k} -->\n{frag}\n<!-- /TABLE -->",
                         txt, flags=re.S)
        open(a.report, "w").write(txt)
    print({k: len(v[1]) for k, v in T.items()})


if __name__ == "__main__":
    main()
