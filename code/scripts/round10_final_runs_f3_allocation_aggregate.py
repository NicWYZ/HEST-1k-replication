"""Round 10, track final-runs, F3.3 (iii): aggregate the allocation units (plan 5d.3 (iii)).

usage: round10_final_runs_f3_allocation_aggregate.py <designs_dir> <out_dir> <r5_e5_allocation_csv>
Writes f3_allocation_units.csv, f3_allocation_checks.csv (per population and estimand: the cluster-value check against
F2, the agreement of A and B0 with round 5's components_part, and the comparison with round 5's e3_components.csv on
the log1p rows), f3_allocation_vs_r5.csv (HEST and ACS theta3 rows at round 5's n_L, round 5's clipped-coefficient
values beside the fixed-coefficient ones) and f3_allocation_rows.csv.
"""
import glob, json, os, sys
import numpy as np, pandas as pd


def unit_status(d):
    p = os.path.join(d, "PROVENANCE.txt")
    if not os.path.exists(p):
        return None, None
    kv = dict(l.split(": ", 1) for l in open(p).read().splitlines() if ": " in l and not l.startswith(" "))
    return kv.get("status"), kv.get("slurm_job_id")

UNITS = ("alloc_hest_log1p", "alloc_hest_normrefit", "alloc_corpus_a", "alloc_corpus_b")


def main(bd, out, e5):
    os.makedirs(out, exist_ok=True)
    units, parts, chk = [], [], []
    for u in UNITS:
        d = os.path.join(bd, u); st, sid = unit_status(d); n = 0
        if st == "COMPLETED":
            x = pd.read_csv(os.path.join(d, "allocation_rows.csv")); n = len(x); parts.append(x)
            s = json.load(open(os.path.join(d, "allocation_summary.json")))
            for p in s["populations"]:
                if "error" in p:
                    chk.append(dict(unit=u, task=p["task"], encoder=p["encoder"], scale=p["scale"], error=p["error"])); continue
                for e, v in p["estimands"].items():
                    cv = v.get("cv_check") or {}
                    chk.append(dict(unit=u, task=p["task"], encoder=p["encoder"], scale=p["scale"], estimand=e, G_valid=v["G_valid"],
                                    cv_n_common=cv.get("n_common"), cv_n_donors=cv.get("n_donors_cv"), cv_max_rel=cv.get("max_rel"),
                                    d_A=v["d_A_vs_components_part"], d_B0=v["d_B0_vs_components_part"]))
            r5 = pd.read_csv(os.path.join(d, "r5_components_check.csv")) if os.path.getsize(os.path.join(d, "r5_components_check.csv")) > 2 else pd.DataFrame()
            if len(r5):
                g = r5.groupby(["task", "encoder", "scale", "estimand"]).max_rel.max().rename("r5_components_max_rel").reset_index()
                for row in g.to_dict("records"):
                    chk.append(dict(unit=u, **row))
        units.append(dict(unit=u, status=st, slurm_job_id=sid, rows=n))
    pd.DataFrame(units).to_csv(os.path.join(out, "f3_allocation_units.csv"), index=False)
    C = pd.DataFrame(chk); C.to_csv(os.path.join(out, "f3_allocation_checks.csv"), index=False)
    a = pd.concat(parts, ignore_index=True)
    r = pd.read_csv(e5).rename(columns={"vtag": "task", "arm": "encoder"})
    r["encoder"] = r.encoder.replace({"package": "pkg"})
    b = a[(a.estimand == "theta3") & (a.gene_scope == "all") & a.scale.isin(["log1p", "log_income"])]
    m = r.merge(b, on=["task", "encoder", "n_L"], how="left", suffixes=("_r5", "_r10"))
    m.to_csv(os.path.join(out, "f3_allocation_vs_r5.csv"), index=False)
    a.to_csv(os.path.join(out, "f3_allocation_rows.csv"), index=False)
    print(json.dumps(dict(units=units, rows=len(a), checks=len(C),
                          cv_max_rel=float(pd.to_numeric(C.get("cv_max_rel"), errors="coerce").max()) if len(C) else None,
                          r5_components_max_rel=float(pd.to_numeric(C.get("r5_components_max_rel"), errors="coerce").max()) if "r5_components_max_rel" in C else None), indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
