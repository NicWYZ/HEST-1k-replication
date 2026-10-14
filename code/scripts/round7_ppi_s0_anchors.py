"""Round 7 inference track, S0: score the two anchors (plan sections 1.1 and 3, track document section 7, S0.3).

Reads, under --s0-dir, arm1/<vtag>/ (round 5's E4b script rerun from this track's snapshot with round 5's seeds) and
arm2/<vtag>/ (round7_ppi_d2.py), the anchor targets from results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv
in --clone, and round 5's threshold medians from results/round5/ppi/E4b_rejective/_threshold/ under --root.
Writes s0_anchors.csv in the working directory.

Arm 1 computes wr_D0cl as round5_ppi_e4b_merge.py does: gene rows with all draws (n_sub > 200), the rej_t width of
D2 (balance, p_a) over the D0 classical width (rule none, textbook_t|fpc|lin), median over genes. It passes when it
equals the target to four decimals. Arm 2 has two rows. 'round5_draws' replays E4b's selection through the new code
path and must equal arm 1 (difference reported). 'new_draws' passes when |value - target| <= 2 sqrt(se_r5^2 + se_new^2),
with both standard errors from the bootstrap over draws in round7_ppi_d2.py.
"""
import argparse
import glob
import os

import numpy as np
import pandas as pd

ANCHORS = [dict(vtag="CCRCC", arm="uni_v2"), dict(vtag="ACS_STATES", arm="package")]
CELL = dict(estimand="theta3", n_L=8, balance="own", p_a=0.01)
LIN = "textbook_t|fpc|lin"


def arm1_value(d, vtag, arm):
    g = pd.read_csv(glob.glob(os.path.join(d, f"e4b_rejective_genes__{vtag}__{arm}.csv.gz"))[0])
    g = g[(g["n_sub"] > 200) & (g["estimand"] == CELL["estimand"]) & (g["n_L"] == CELL["n_L"])]
    d0 = g[(g["design"] == "D0") & (g["rule"] == "none") & (g["interval"] == LIN)][["gene", "width"]]
    rj = g[(g["design"] == "D2") & (g["interval"] == "rej_t") & (g["balance"] == CELL["balance"])
           & np.isclose(g["p_a"], CELL["p_a"])][["gene", "width"]]
    w = rj.merge(d0, on="gene", suffixes=("", "_D0cl"))
    return float(np.median(w["width"] / w["width_D0cl"])), len(w)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--s0-dir", required=True)
    p.add_argument("--clone", default="/work/users/w/e/weiyang/hest_code/round7-ppi")
    p.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    a = p.parse_args(argv)
    tg = pd.read_csv(os.path.join(a.clone, "results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv"))
    rows = []
    for an in ANCHORS:
        vt, arm = an["vtag"], an["arm"]
        t = tg[(tg["vtag"] == vt) & (tg["arm"] == arm) & (tg["estimand"] == CELL["estimand"]) & (tg["n_L"] == CELL["n_L"])
               & (tg["balance"] == CELL["balance"]) & np.isclose(tg["p_a"], CELL["p_a"])]
        assert len(t) == 1, (vt, arm, len(t))
        target = float(t["wr_D0cl"].iloc[0])
        v1, ng1 = arm1_value(os.path.join(a.s0_dir, "arm1", vt), vt, arm)
        a2 = pd.read_csv(os.path.join(a.s0_dir, "arm2", vt, f"s0_arm2__{vt}__{arm}.csv"))
        r5 = a2[a2["draws_kind"] == "round5_draws"].iloc[0]
        nw = a2[a2["draws_kind"] == "new_draws"].iloc[0]
        th = pd.read_csv(os.path.join(a.s0_dir, "arm2", vt, f"s0_thresholds__{vt}__{arm}.csv"))
        thr5 = pd.read_csv(os.path.join(a.root, "results/round5/ppi/E4b_rejective/_threshold", vt, arm,
                                        f"e4b_threshold__{vt}__{arm}.csv"))
        thr5 = thr5[(thr5["estimand"] == CELL["estimand"]) & (thr5["n_L"] == CELL["n_L"]) & (thr5["balance"] == CELL["balance"])
                    & np.isclose(thr5["p_a"], CELL["p_a"])]
        thr_med5 = float(thr5["thr_E4b_median"].iloc[0])
        thr_med7 = float(np.median(th["threshold"]))
        base = dict(CELL, vtag=vt, arm=arm, target_wr_D0cl=target, threshold_median_round7=thr_med7,
                    threshold_median_round5=thr_med5, threshold_median_ratio=thr_med7 / thr_med5)
        rows.append(dict(base, anchor_arm="arm1_round5_code", value=v1, n_genes=ng1, se=np.nan,
                         diff=v1 - target, tolerance="equal to four decimals",
                         passed=bool(round(v1, 4) == round(target, 4))))
        rows.append(dict(base, anchor_arm="arm2_round5_draws_new_code", value=float(r5["wr_D0cl"]),
                         n_genes=int(r5["n_genes"]), se=float(r5["boot_se"]), diff=float(r5["wr_D0cl"]) - v1,
                         tolerance="equal to arm 1 to 1e-9", passed=bool(abs(float(r5["wr_D0cl"]) - v1) <= 1e-9)))
        sd = float(np.sqrt(r5["boot_se"] ** 2 + nw["boot_se"] ** 2))
        rows.append(dict(base, anchor_arm="arm2_new_draws", value=float(nw["wr_D0cl"]), n_genes=int(nw["n_genes"]),
                         se=float(nw["boot_se"]), diff=float(nw["wr_D0cl"]) - target,
                         tolerance=f"2 x sqrt(se_r5^2 + se_new^2) = {2 * sd:.6f}",
                         z=(float(nw["wr_D0cl"]) - target) / sd, passed=bool(abs(float(nw["wr_D0cl"]) - target) <= 2 * sd)))
    pd.DataFrame(rows).to_csv("s0_anchors.csv", index=False, float_format="%.10g")
    print(pd.DataFrame(rows)[["vtag", "anchor_arm", "value", "target_wr_D0cl", "diff", "passed"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
