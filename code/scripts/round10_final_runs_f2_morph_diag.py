"""Round 10, track final-runs, F2 option (b): why kidney Visium's spot features differ from KIDNEY_POP54_morph.parquet.

Per sample, on shared (sample_id, barcode): median ratio of n_nuclei (reference over ours), share of rows equal on
n_nuclei, and for the CCRCC samples the per-spot correlation of our area_mean with round 3's CCRCC prediction file's
area_mean (benchmark patches, so equality is not expected).
usage: round10_final_runs_f2_morph_diag.py <ours.parquet> <KIDNEY_POP54_morph.parquet> <round3 CCRCC predictions> <out_dir>
"""
import sys, os, json, numpy as np, pandas as pd
ours, ref, r3, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
A = pd.read_parquet(ours); B = pd.read_parquet(ref)
m = A.merge(B, on=["sample_id", "barcode"], suffixes=("", "_ref"))
rows = []
for sid, g in m.groupby("sample_id"):
    ok = (g.n_nuclei > 0) & (g.n_nuclei_ref > 0)
    rows.append(dict(sample_id=sid, n=len(g), frac_equal_n_nuclei=float((g.n_nuclei == g.n_nuclei_ref).mean()),
                     median_ratio_n_nuclei=float((g.n_nuclei_ref[ok] / g.n_nuclei[ok]).median()) if ok.any() else np.nan,
                     median_ratio_area_mean=float((g.area_mean_ref[ok] / g.area_mean[ok]).median()) if ok.any() else np.nan,
                     ref_task=str(g.task_ref.iloc[0]) if "task_ref" in g else ""))
pd.DataFrame(rows).to_csv(os.path.join(out, "morph_diag_vs_pop54.csv"), index=False)
C = pd.read_parquet(r3, columns=["sample_id", "barcode", "area_mean", "frac_neoplastic"])
c = A.merge(C, on=["sample_id", "barcode"], suffixes=("", "_r3"))
ok = np.isfinite(c.area_mean) & np.isfinite(c.area_mean_r3)
res = dict(n_shared_with_round3=len(c), n_both_finite=int(ok.sum()),
           corr_area_mean=float(np.corrcoef(c.area_mean[ok], c.area_mean_r3[ok])[0, 1]) if ok.sum() > 2 else None,
           median_ratio_area_mean=float((c.area_mean_r3[ok] / c.area_mean[ok]).median()) if ok.any() else None,
           corr_frac_neoplastic=float(np.corrcoef(c.frac_neoplastic[ok], c.frac_neoplastic_r3[ok])[0, 1]) if ok.sum() > 2 else None,
           frac_equal_area_mean=float((np.abs(c.area_mean[ok] - c.area_mean_r3[ok]) < 1e-6).mean()) if ok.any() else None)
json.dump(res, open(os.path.join(out, "morph_diag_vs_round3.json"), "w"), indent=1)
print(pd.DataFrame(rows).to_string()); print(json.dumps(res, indent=1))
