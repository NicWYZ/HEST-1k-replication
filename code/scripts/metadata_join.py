#!/usr/bin/env python
"""Stage 4a: join real HEST sample metadata onto the instrumentation tables.

handoff 4a requires sample metadata from HEST's metadata CSV: patient, cohort source, technology,
organ, oncotree code, tissue preparation, species. Until now the instrumentation tables carried
cohort and technology DERIVED by me -- cohort from the sample-ID letter prefix, technology from a
hardcoded set of task names. Both are now replaced by the metadata and, more importantly, the
derived values are AUDITED against it: a derived label that silently disagreed would have
propagated into the 4b site-shift arms and the 4d probes, which are built on exactly these two
variables.

Column mapping (HEST_v1_1_0.csv, 28 columns, covers 72/72 benchmark samples):
  patient             <- patient
  technology          <- st_technology          (audited against my task-based Xenium/Visium guess)
  organ               <- organ
  oncotree_code       <- oncotree_code
  species             <- species
  tissue_preparation  <- preservation_method, plus `tissue`
  cohort source       <- there is NO literal column. dataset_title and subseries identify the
                         study; the sample-ID prefix (INT/MEND/TENX/NCBI/ZEN) identifies the
                         source collection. Both are carried, and the prefix is checked for
                         consistency against dataset_title so "cohort source" is defined by data
                         rather than by my parsing.
Also carried because the morphology work needed them: pixel_size_um_estimated, spot_diameter,
inter_spot_dist, magnification.
"""
import os, glob, re
import numpy as np, pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, OUT = f"{ROOT}/bench_data", f"{ROOT}/instrumentation"
META = f"{ROOT}/code/HEST/assets/HEST_v1_1_0.csv"
KEEP = ["patient","st_technology","organ","oncotree_code","species","preservation_method",
        "tissue","disease_state","dataset_title","subseries","pixel_size_um_estimated",
        "spot_diameter","inter_spot_dist","magnification","spots_under_tissue","nb_genes"]

m = pd.read_csv(META, low_memory=False)
m["id"] = m["id"].astype(str)

samples = []
for p in sorted(glob.glob(f"{BD}/*/adata/*.h5ad")):
    samples.append(dict(task=p.split("/bench_data/")[1].split("/")[0],
                        sample_id=os.path.basename(p)[:-5]))
s = pd.DataFrame(samples)
j = s.merge(m[["id"]+KEEP], left_on="sample_id", right_on="id", how="left", indicator=True)
# distinguish a FAILED JOIN (sample absent from the metadata) from a NULL FIELD (row present,
# value not annotated). Conflating them would have reported a missing row for TENX111, whose row
# exists but carries no patient id.
unjoined = j.loc[j._merge != "both", "sample_id"].tolist()
assert not unjoined, f"samples absent from metadata: {unjoined}"
j = j.drop(columns=["id","_merge"])
print(f"joined metadata for {len(j)}/{len(s)} samples, {j.task.nunique()} tasks")
nulls = j[KEEP].isna().sum()
nulls = nulls[nulls > 0].sort_values(ascending=False)
print(f"\n=== null fields (row present, value not annotated) ===")
print(nulls.to_string() if len(nulls) else "  none")
for col in nulls.index:
    who = j.loc[j[col].isna(), ["task","sample_id"]]
    if len(who) <= 6:
        print(f"  {col}: {[f'{r.task}/{r.sample_id}' for _,r in who.iterrows()]}")
    else:
        print(f"  {col}: {len(who)} samples, tasks {sorted(who.task.unique())}")

# ---- AUDIT 1: technology. My earlier label was a hardcoded task set. ----
XEN_GUESS = {"IDC","PAAD","SKCM","COAD","LUNG"}
j["technology_derived"] = np.where(j.task.isin(XEN_GUESS), "Xenium", "Visium")
j["technology"] = j.st_technology.astype(str)
agree = j.technology.str.contains("Xenium", case=False) == (j.technology_derived == "Xenium")
print(f"\n=== AUDIT 1: technology, derived vs metadata ===")
print(f"  agree: {int(agree.sum())}/{len(j)}")
print(j.groupby(["task","st_technology"]).size().rename("n").reset_index().to_string(index=False))
if not agree.all():
    print("  DISAGREEMENTS:")
    print(j.loc[~agree, ["task","sample_id","technology_derived","st_technology"]].to_string(index=False))

# ---- AUDIT 2: cohort source. My earlier label was the sample-ID letter prefix. ----
j["cohort_prefix"] = j.sample_id.str.extract(r"^([A-Za-z]+)")[0]
print(f"\n=== AUDIT 2: cohort source, ID prefix vs dataset_title ===")
xt = j.groupby(["cohort_prefix","dataset_title"]).size().rename("n").reset_index()
print(xt.to_string(index=False))
per_prefix = j.groupby("cohort_prefix").dataset_title.nunique()
print(f"\n  distinct dataset_title per prefix: {per_prefix.to_dict()}")
print(f"  prefix is a 1:1 proxy for study: {bool((per_prefix==1).all())}")
per_title = j.groupby("dataset_title").cohort_prefix.nunique()
print(f"  studies spanning >1 prefix: {int((per_title>1).sum())}")

# ---- AUDIT 3: patient. Does the shipped fold structure respect patient, or slide? ----
print(f"\n=== AUDIT 3: patient vs slide ===")
pp = j.groupby("task").agg(samples=("sample_id","size"), patients=("patient","nunique"),
                           patient_nulls=("patient", lambda x: int(x.isna().sum())))
folds = {}
for t in sorted(j.task.unique()):
    folds[t] = len(glob.glob(f"{BD}/{t}/splits/test_*.csv"))
pp["shipped_folds"] = pd.Series(folds)
# nunique() skips nulls, so a task with unannotated patients would look like it had fewer
pp["one_slide_per_patient"] = (pp.samples == pp.patients) & (pp.patient_nulls == 0)
print(pp.to_string())
print(f"  tasks where slides outnumber patients: "
      f"{pp.index[~pp.one_slide_per_patient].tolist()}")

# ---- AUDIT 4: preservation / tissue, the handoff's "tissue preparation" ----
print(f"\n=== AUDIT 4: tissue preparation ===")
print(j.groupby(["st_technology","preservation_method"]).size().rename("n").reset_index().to_string(index=False))
print(f"\n  organs: {sorted(j.organ.dropna().unique())}")
print(f"  oncotree codes: {sorted(j.oncotree_code.dropna().unique())}")
print(f"  species: {j.species.value_counts().to_dict()}")

j.to_csv(f"{OUT}/sample_metadata.csv", index=False)
print(f"\nwrote {OUT}/sample_metadata.csv  ({len(j)} rows x {len(j.columns)} cols)")
