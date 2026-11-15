"""Round 10, track final-runs, F2.0 anchor 2: theta3 and theta2 donor values against round 5's own construction.

Round 5's E4b unit forms donor values with round5_ppi_e4_selection.donor_arrays (round 4's z_arrays with B1's
per-donor design constants) on the arm loaded by round5_ppi_e2_regimeB.load_arm. This script imports those
unchanged from the snapshot of round 5's commit (PYTHONPATH set by the job, first entry) and compares them with
this track's cluster values for the same task, encoder and estimand, on log(1 + y).
usage: round10_final_runs_f2_anchor_r5.py <cluster_values.parquet> <prediction parquet> <vtag> <arm> <out_dir>
"""
import sys, os, json, numpy as np, pandas as pd
from round5_ppi_e2_regimeB import load_arm
from round5_ppi_e4_selection import donor_arrays
cvp, pq_, vtag, arm, out = sys.argv[1:6]; os.makedirs(out, exist_ok=True)
data = load_arm(pq_, arm, vtag)
cv = pd.read_parquet(cvp)
rows = []
for est in ("theta3", "theta2"):
    zb, fb, ok = donor_arrays(data, est)
    donors = [str(d) for d in data["donors"]]; genes = list(data["genes"])
    mine = cv[(cv.estimand == est) & (cv.encoder == arm) & (cv.scale == "log1p")]
    Z = mine.pivot(index="donor", columns="gene", values="z"); F = mine.pivot(index="donor", columns="gene", values="f")
    vd = [d for d, o in zip(donors, ok) if o]
    idx = [donors.index(d) for d in vd]
    common = [d for d in vd if d in Z.index]
    zr = zb[[donors.index(d) for d in common]][:, [genes.index(g) for g in Z.columns]]
    fr = fb[[donors.index(d) for d in common]][:, [genes.index(g) for g in Z.columns]]
    zm, fm = Z.loc[common].to_numpy(), F.loc[common].to_numpy()
    rel = lambda a, b: float(np.nanmax(np.abs(a - b) / np.maximum(1e-12, np.abs(b))))
    rows.append(dict(estimand=est, vtag=vtag, arm=arm, donors_r5_valid=len(vd), donors_ours=int(Z.shape[0]),
                     donors_common=len(common), genes=int(Z.shape[1]), max_rel_z=rel(zm, zr), max_rel_f=rel(fm, fr),
                     max_abs_z=float(np.nanmax(np.abs(zm - zr))), max_abs_f=float(np.nanmax(np.abs(fm - fr))),
                     donors_only_r5=";".join(sorted(set(vd) - set(Z.index))), donors_only_ours=";".join(sorted(set(Z.index) - set(vd)))))
pd.DataFrame(rows).to_csv(os.path.join(out, "f2_anchor_r5.csv"), index=False)
print(pd.DataFrame(rows).to_string())
