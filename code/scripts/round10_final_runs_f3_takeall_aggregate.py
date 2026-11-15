"""Round 10, track final-runs, F3.3 (v): aggregate the take-all units and compare with round 9 (plan 5d.3 (v)).

usage: round10_final_runs_f3_takeall_aggregate.py <designs_dir> <out_dir> <r9_takeall_medians_csv>
Reads every takeall_<unit> directory whose PROVENANCE.txt reads COMPLETED (smoke, anchor and aggregate excluded).\nWrites f3_takeall_units.csv, f3_takeall_vs_r9.csv (round 9's tasks, uni_v2, log1p, mu, gene scope all, every k and
n_L: round 9's T0 and D0 medians beside round 10's T0, T0_fix1, D0 and D0_fix1) and f3_takeall_cells.csv.
"""
import glob, json, os, sys
import numpy as np, pandas as pd


def unit_status(d):
    p = os.path.join(d, "PROVENANCE.txt")
    if not os.path.exists(p):
        return None, None
    kv = dict(l.split(": ", 1) for l in open(p).read().splitlines() if ": " in l and not l.startswith(" "))
    return kv.get("status"), kv.get("slurm_job_id")


def main(bd, out, r9):
    os.makedirs(out, exist_ok=True)
    units, parts = [], []
    for d in sorted(glob.glob(os.path.join(bd, "takeall_*"))):
        u = os.path.basename(d)
        if u in ("takeall_smoke", "takeall_aggregate") or u.startswith("takeall_anchor"):
            continue
        st, sid = unit_status(d)
        f = os.path.join(d, "takeall_cells.csv"); n = 0
        if st == "COMPLETED" and os.path.exists(f):
            x = pd.read_csv(f); n = len(x); parts.append(x)
        units.append(dict(unit=u, status=st, slurm_job_id=sid, rows=n))
    pd.DataFrame(units).to_csv(os.path.join(out, "f3_takeall_units.csv"), index=False)
    c = pd.concat(parts, ignore_index=True)
    ref = pd.read_csv(r9)
    x = c[(c.encoder == "uni_v2") & (c.scale == "log1p") & (c.estimand == "mu") & (c.gene_scope == "all") & c.task.isin(ref.task.unique())]
    w = x.pivot_table(index=["task", "k", "n_L"], columns="method", values="median_coverage").add_prefix("r10_cov_")
    ww = x.pivot_table(index=["task", "k", "n_L"], columns="method", values="median_wr_D0").add_prefix("r10_wrD0_")
    r = ref.pivot_table(index=["task", "k", "n_L"], columns="method", values="median_coverage").add_prefix("r9_cov_")
    rw = ref.pivot_table(index=["task", "k", "n_L"], columns="method", values="median_width_ratio").add_prefix("r9_wrD0_")
    m = r.join(rw).join(w, how="left").join(ww, how="left").reset_index()
    m.to_csv(os.path.join(out, "f3_takeall_vs_r9.csv"), index=False)
    c.to_csv(os.path.join(out, "f3_takeall_cells.csv"), index=False)
    print(json.dumps(dict(units=units, cell_rows=len(c)), indent=1)); print(m.round(4).to_string())


if __name__ == "__main__":
    main(*sys.argv[1:4])
