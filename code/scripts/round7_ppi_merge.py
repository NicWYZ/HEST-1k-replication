"""Round 7 inference track: merge the S1 or S2 unit fragments (track document section 4, fan-out).

--stage S1 reads results/round7/ppi/S1_weighting/<task>/<arm>_nL<n>/ and .../sim/<tag>/ under --root and writes, in
the working directory, s1_stamp_check.csv, s1_masking_grid.csv (one row per cell and interval, with the median over
genes of the per-gene width ratio to the D0 classical interval of the same task, arm, estimand and n_L, as round 5's
wr_D0cl), s1_masking_diag.csv, s1_skipped.csv, s1_sim.csv (with the width ratio to D0 classical of the same
simulation cell) and s1_pi_hat.parquet.
--stage S2 reads results/round7/ppi/S2_comparators/... and writes s2_stamp_check.csv, s2_masking_grid.csv (with the
width ratio to D0 classical textbook_t|fpc|lin of the same set) and s2_sim.csv.
The stamp check compares the frame id of every unit directory's _provenance.json with the id the lead assigned
(results/round7/ppi/<stage dir>/<stage>_assigned_frame_ids.csv in --clone). A directory whose id differs, or whose
PROVENANCE.txt is not COMPLETED, is listed and left out of the merge.
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

LIN = "textbook_t|fpc|lin"


def stamps(base, assigned, units):
    rows, ok = [], []
    for task in units:
        for d in sorted(glob.glob(os.path.join(base, task, "*"))):
            if not os.path.isdir(d) or os.path.basename(d).startswith("_"):
                continue
            fid = json.load(open(os.path.join(d, "_provenance.json")))["frame_id"] if os.path.exists(os.path.join(d, "_provenance.json")) else ""
            prov = open(os.path.join(d, "PROVENANCE.txt")).read() if os.path.exists(os.path.join(d, "PROVENANCE.txt")) else ""
            st = "COMPLETED" if "status: COMPLETED" in prov else "missing or failed"
            jid = next((l.split(": ")[1] for l in prov.splitlines() if l.startswith("slurm_job_id:")), "")
            good = fid == assigned.get(task) and st == "COMPLETED"
            rows.append(dict(task=task, dir=os.path.relpath(d, base), slurm_job_id=jid, frame_id=fid,
                             assigned=assigned.get(task, ""), status=st, merged=good))
            if good:
                ok.append(d)
    return pd.DataFrame(rows), ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("S1", "S2"), required=True)
    ap.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    ap.add_argument("--clone", default="/work/users/w/e/weiyang/hest_code/round7-ppi")
    a = ap.parse_args()
    sd = "S1_weighting" if a.stage == "S1" else "S2_comparators"
    base = os.path.join(a.root, "results/round7/ppi", sd)
    asg = pd.read_csv(os.path.join(a.clone, "results/round7/ppi", sd, f"{a.stage.lower()}_assigned_frame_ids.csv"))
    assigned = dict(zip(asg["unit"], asg["frame_id"]))
    tasks = [t for t in assigned if t != "sim"]
    st, dirs = stamps(base, assigned, tasks + ["sim"])
    st.to_csv(f"{a.stage.lower()}_stamp_check.csv", index=False)
    mdirs = [d for d in dirs if "/sim/" not in d]
    sdirs = [d for d in dirs if "/sim/" in d]
    p = "s1m" if a.stage == "S1" else "s2m"
    cells = pd.concat([pd.read_csv(f) for d in mdirs for f in glob.glob(os.path.join(d, f"{p}_cells__*.csv"))], ignore_index=True)
    genes = pd.concat([pd.read_csv(f, low_memory=False) for d in mdirs for f in glob.glob(os.path.join(d, f"{p}_genes__*.csv.gz"))],
                      ignore_index=True)
    if a.stage == "S1":
        key = ["vtag", "arm", "estimand", "n_L", "gene"]
        d0 = genes[(genes["design"] == "D0") & (genes["estimator"] == "classical") & (genes["variance"] == LIN)][key + ["width", "coverage"]]
        g = genes.merge(d0.rename(columns={"width": "width_D0cl", "coverage": "coverage_D0cl"}), on=key, how="left")
        g["wr_D0cl"] = g["width"] / g["width_D0cl"]
        ck = ["vtag", "arm", "estimand", "n_L", "design", "balance", "p_a", "estimator", "variance", "ref"]
        wr = g.groupby(ck, dropna=False).agg(wr_D0cl_median=("wr_D0cl", "median"),
                                             coverage_D0cl_median=("coverage_D0cl", "median")).reset_index()
        grid = cells.merge(wr, on=ck, how="left")
        grid.to_csv("s1_masking_grid.csv", index=False, float_format="%.10g")
        pd.concat([pd.read_csv(f) for d in mdirs for f in glob.glob(os.path.join(d, "s1m_diag__*.csv"))],
                  ignore_index=True).to_csv("s1_masking_diag.csv", index=False, float_format="%.10g")
        sk = [pd.read_csv(f).assign(dir=os.path.relpath(d, base)) for d in mdirs for f in glob.glob(os.path.join(d, "s1m_skipped__*.csv"))
              if os.path.getsize(f) > 2]
        (pd.concat(sk, ignore_index=True) if sk else pd.DataFrame()).to_csv("s1_skipped.csv", index=False)
        tabs = [pq.read_table(f) for d in mdirs for f in glob.glob(os.path.join(d, "s1m_pi__*.parquet"))]
        import pyarrow as pa
        pq.write_table(pa.concat_tables(tabs), "s1_pi_hat.parquet")
        if sdirs:
            sim = pd.concat([pd.read_csv(f) for d in sdirs for f in glob.glob(os.path.join(d, "s1_sim__*.csv"))], ignore_index=True)
            sk_ = ["G", "n_L", "R2", "lambda_star", "law", "k"]
            d0s = sim[(sim["design"] == "D0") & (sim["estimator"] == "classical") & (sim["variance"] == LIN)][sk_ + ["width_mean", "coverage_mean"]]
            sim = sim.merge(d0s.rename(columns={"width_mean": "width_D0cl", "coverage_mean": "coverage_D0cl"}), on=sk_, how="left")
            sim["wr_D0cl"] = sim["width_mean"] / sim["width_D0cl"]
            sim.to_csv("s1_sim.csv", index=False, float_format="%.10g")
    else:
        key = ["vtag", "arm", "estimand", "n_L", "set", "gene"]
        d0 = genes[(genes["design"] == "D0") & (genes["estimator"] == "classical") & (genes["interval"] == LIN)][key + ["width"]]
        g = genes.merge(d0.rename(columns={"width": "width_D0cl"}), on=key, how="left")
        g["wr_D0cl"] = g["width"] / g["width_D0cl"]
        ck = ["vtag", "arm", "estimand", "n_L", "set", "design", "estimator", "interval"]
        wr = g.groupby(ck).agg(wr_D0cl_median=("wr_D0cl", "median")).reset_index()
        cells.merge(wr, on=ck, how="left").to_csv("s2_masking_grid.csv", index=False, float_format="%.10g")
        if sdirs:
            sim = pd.concat([pd.read_csv(f) for d in sdirs for f in glob.glob(os.path.join(d, "s2_sim__*.csv"))], ignore_index=True)
            sk_ = ["G", "n_L", "R2", "lambda_star", "law"]
            d0s = sim[(sim["design"] == "D0") & (sim["estimator"] == "classical") & (sim["interval"] == LIN)][sk_ + ["width_mean"]]
            sim = sim.merge(d0s.rename(columns={"width_mean": "width_D0cl"}), on=sk_, how="left")
            sim["wr_D0cl"] = sim["width_mean"] / sim["width_D0cl"]
            sim.to_csv("s2_sim.csv", index=False, float_format="%.10g")
    print(len(st), int(st["merged"].sum()), len(cells))


if __name__ == "__main__":
    main()
