#!/usr/bin/env python
"""Stage 4e QC + join key check, restricted to the spots that actually carry predictions.

Two things the per-sample summary CANNOT answer, because it counts over all AnnData spots while
only the patch subset has embeddings/predictions:
  1. spot coverage -- what fraction of PREDICTED spots have >=1 nucleus. The summary's
     spots_with_nuclei is over all AnnData spots and for several samples EXCEEDS n_patch_spots,
     so any ratio built from those two columns mixes populations. This is the same
     mismatched-denominator error as v1's n_spots column; the build records in_patch_set so it
     can be done correctly.
  2. whether the morphology table joins 1:1 onto the 4a prediction tables on (sample_id, barcode).
"""
import glob, os
import numpy as np, pandas as pd
ROOT = "/work/users/w/e/weiyang/hest_replication"
IN, DATA = f"{ROOT}/instrumentation/morphology", f"{ROOT}/instrumentation"
OUT = f"{ROOT}/results/tailored/morphology"
FEATS = ["n_nuclei","area_mean","area_median","n_neoplastic","neo_area_mean",
         "frac_neoplastic","frac_inflammatory","frac_connective","frac_epithelial","frac_dead"]
rows = []
for p in sorted(glob.glob(f"{IN}/*_morph.parquet")):
    task = os.path.basename(p).replace("_morph.parquet","")
    m = pd.read_parquet(p)
    inp = m[m.in_patch_set]
    sp = pd.read_parquet(f"{DATA}/{task}/spots.parquet", columns=["sample_id","barcode"])
    sp_keys = set(zip(sp.sample_id.astype(str), sp.barcode.astype(str)))
    m_keys  = set(zip(inp.sample_id.astype(str), inp.barcode.astype(str)))
    rows.append(dict(
        task=task, morph_rows=len(m), in_patch=len(inp),
        pred_spots=len(sp_keys), join_matched=len(sp_keys & m_keys),
        join_complete=(sp_keys <= m_keys),
        dup_keys=int(len(inp) - len(m_keys)),
        cov_all_adata=round(float((m.n_nuclei > 0).mean()), 4),
        cov_predicted=round(float((inp.n_nuclei > 0).mean()), 4),
        median_nuc=float(inp.n_nuclei.median()),
        zero_nuc_predicted=int((inp.n_nuclei == 0).sum()),
        frac_sum_ok=bool(np.allclose(
            inp.loc[inp.n_nuclei > 0, [c for c in FEATS if c.startswith("frac_")]].sum(axis=1), 1.0,
            atol=1e-6)),
        neo_nan_when_absent=bool(inp.loc[inp.n_neoplastic == 0, "neo_area_mean"].isna().all()),
    ))
    print(f"  {task}: {len(m):,} rows, {len(inp):,} in patch set, "
          f"coverage {(inp.n_nuclei>0).mean():.3f} vs {(m.n_nuclei>0).mean():.3f} over all adata",
          flush=True)
d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/morphology_qc.csv", index=False)
print()
print(d[["task","in_patch","pred_spots","join_matched","join_complete","dup_keys",
         "cov_predicted","cov_all_adata","zero_nuc_predicted"]].to_string(index=False))
print(f"\njoin is complete for every task: {bool(d.join_complete.all())}")
print(f"duplicate (sample_id,barcode) keys: {int(d.dup_keys.sum())}")
print(f"class fractions sum to 1 where nuclei exist: {bool(d.frac_sum_ok.all())}")
print(f"neo_area_mean is NaN (not 0) where no neoplastic nuclei: {bool(d.neo_nan_when_absent.all())}")
print(f"\ncoverage over PREDICTED spots: {d.cov_predicted.min():.3f}-{d.cov_predicted.max():.3f} "
      f"(weighted {np.average(d.cov_predicted, weights=d.in_patch):.4f})")
print(f"coverage over ALL adata spots : {d.cov_all_adata.min():.3f}-{d.cov_all_adata.max():.3f} "
      f"-- the misleading denominator")
print(f"predicted spots with ZERO nuclei: {int(d.zero_nuc_predicted.sum()):,} of "
      f"{int(d.in_patch.sum()):,} ({100*d.zero_nuc_predicted.sum()/d.in_patch.sum():.2f}%) "
      f"-- these get NaN morphology, not imputed zeros")
