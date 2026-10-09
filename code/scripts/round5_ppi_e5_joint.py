"""Round 5 PPI, interval 3, E5 item 3: the joint design table (memo E4 decisions section 5; plan 8.5).

results/round5/ppi/E5_joint/e5_joint_design.csv, long format, one block of rows per task and
m in {5, 10, 15, 20, 25, 50, 100}:

  block = inference       one row per task, arm (encoders; package on ACS), estimand and m: regime B,
                          every cluster labelled with m units (n_L = G), design target, interval regB_t,
                          form C. width_ratio is the median over genes of the C_ppi width over the
                          C_classical width (gene rows of E3/<task>/<arm>__regb/e3_regb_genes__*.csv.gz);
                          coverage_C_ppi and coverage_C_classical are medians over genes.
                          min_units_ok is m >= 3 for theta3 and m >= 4 for the stratified theta2 (the
                          smallest numbers of labelled units per cluster the form needs); clusters with
                          fewer units than m are labelled completely by the E3 draw.
  block = prediction_set  one row per tissue task, m, W3 part and K: the narrowest valid prediction set
                          at o = m and alpha = 0.1 (narrowest_valid in w3_map_by_task.csv), its method,
                          coverage and width, read from origin/main by `git show` (--w3-commit records
                          the commit). Tasks map CCRCC_23merged to CCRCC_merged. A (task, m, part, K) with
                          no o = m row is absent.
"""
import argparse
import glob
import io
import subprocess

import numpy as np
import pandas as pd

D = "results/round5/ppi/E3_twolevel"
OUT = "results/round5/ppi/E5_joint/e5_joint_design.csv"
MS = (5, 10, 15, 20, 25, 50, 100)
ARMS = ("hoptimus0", "uni_v2", "resnet50", "package")
W3 = "results/round5/conformal/W3_real/merged/w3_map_by_task.csv"
TASKMAP = {"CCRCC_23merged": "CCRCC_merged"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w3-commit", required=True)
    a = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(f"{D}/*/*__regb/e3_regb_genes__*.csv.gz")):
        g = pd.read_csv(f, low_memory=False)
        g = g[g["arm"].isin(ARMS) & g["estimator"].isin(["C_ppi", "C_classical"]) & (g["interval"] == "regB_t")]
        g["m_num"] = pd.to_numeric(g["m"], errors="coerce")
        g = g[g["m_num"].isin(MS)]
        if g.empty:
            continue
        pv = g.pivot_table(index=["vtag", "arm", "estimand", "m_num", "n_L", "gene"], columns="estimator",
                           values=["width", "coverage"])
        pv = pv.dropna()
        pv["wr"] = pv[("width", "C_ppi")] / pv[("width", "C_classical")]
        for (vt, arm, est, m, nL), x in pv.groupby(level=[0, 1, 2, 3, 4]):
            rows.append(dict(block="inference", vtag=vt, arm=arm, estimand=est, m=int(m), n_L=int(nL),
                             n_genes=len(x), width_ratio=float(np.median(x["wr"])),
                             coverage_C_ppi=float(np.median(x[("coverage", "C_ppi")])),
                             coverage_C_classical=float(np.median(x[("coverage", "C_classical")])),
                             min_units_ok=bool(m >= (3 if est == "theta3" else 4))))
    src = subprocess.run(["git", "show", f"{a.w3_commit}:{W3}"], capture_output=True, text=True, check=True).stdout
    w = pd.read_csv(io.StringIO(src))
    w = w[w["narrowest_valid"] & (w["alpha"] == 0.1) & w["o"].isin(MS)]
    for r in w.itertuples():
        rows.append(dict(block="prediction_set", vtag=TASKMAP.get(r.task, r.task), m=int(r.o), w3_part=int(r.part),
                         K=int(r.K), n_T_donors=r.n_T_donors, pset_method=r.method, pset_coverage=r.coverage,
                         pset_coverage_sd_folds=r.coverage_sd_folds, pset_width=r.width_mean,
                         w3_source=f"{a.w3_commit}:{W3}"))
    out = pd.DataFrame(rows).sort_values(["vtag", "m", "block"], kind="stable")
    out.to_csv(OUT, index=False)
    print(out.groupby(["block", "vtag"]).size().to_string())


if __name__ == "__main__":
    main()
