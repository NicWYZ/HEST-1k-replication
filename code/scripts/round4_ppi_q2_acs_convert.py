#!/usr/bin/env python
"""Round 4 PPI Q2: convert the ACS PUMS 2018 predictions to B1's per-spot predictions schema.
ACS_STATES: all filtered persons, donor_id = ST (51 clusters).
ACS_CA_PUMA: persons with ST = 6, donor_id = PUMA.
Columns: sample_id (=donor_id), barcode (SERIALNO_SPORDER), donor_id, joined (True), m_std (AGEP standardised
over the rows of the file, ddof=0), area_mean (AGEP), frac_neoplastic (NaN), y__log_income, f__log_income, fold.
"""
import sys, json, hashlib, os
import numpy as np, pandas as pd
D = sys.argv[1]; OUT = sys.argv[2]
pred = pd.read_parquet(f"{D}/acs_pums2018_predictions.parquet")
allc = pd.read_parquet(f"{D}/acs_pums2018_all_columns.parquet")
print("pred", pred.shape, list(pred.columns)); print("all", allc.shape)
print(pred.dtypes.to_dict()); 
need = ["SERIALNO","SPORDER","AGEP","PINCP","WKHP","PWGTP","ST","PUMA"]
missing = [k for k in need if k not in allc.columns]; assert not missing, missing
a = allc[need].copy()
filt = (a.AGEP > 16) & (a.PINCP > 100) & (a.WKHP > 0) & (a.PWGTP >= 1)
print("rows in all_columns", len(a), "after filter", int(filt.sum()))
a = a[filt]
assert a.duplicated(["SERIALNO","SPORDER"]).sum() == 0
assert pred.duplicated(["SERIALNO","SPORDER"]).sum() == 0
m = pred.merge(a[["SERIALNO","SPORDER","AGEP","PINCP","ST","PUMA"]], on=["SERIALNO","SPORDER"], how="left", suffixes=("","_a"), validate="one_to_one")
assert len(m) == len(pred) == 1659616, (len(m), len(pred))
assert m.AGEP.notna().all()
assert (m.ST == m.ST_a).all() and (m.PUMA == m.PUMA_a).all()
chk = np.abs(np.log(m.PINCP.astype(float)) - m.log_PINCP).max(); print("max |log PINCP - log_PINCP|", chk); assert chk < 1e-9
for c_ in ["log_PINCP","yhat","AGEP"]: assert np.isfinite(m[c_].astype(float)).all()
os.makedirs(OUT, exist_ok=True)
info = {}
def write(df, donor, name):
    df = df.reset_index(drop=True)
    age = df.AGEP.astype(float).to_numpy()
    did = df[donor].astype(int).astype(str)
    o = pd.DataFrame({"sample_id": did, "barcode": df.SERIALNO.astype(str) + "_" + df.SPORDER.astype(int).astype(str),
        "donor_id": did, "joined": True, "m_std": (age - age.mean())/age.std(ddof=0), "area_mean": age,
        "frac_neoplastic": np.nan, "y__log_income": df.log_PINCP.astype(float), "f__log_income": df.yhat.astype(float),
        "fold": df.fold})
    assert not o.barcode.duplicated().any()
    p = f"{OUT}/{name}.parquet"
    assert not os.path.exists(p), p
    o.to_parquet(p, index=False)
    info[name] = dict(rows=len(o), clusters=int(o.donor_id.nunique()), age_mean=float(age.mean()), age_sd_ddof0=float(age.std(ddof=0)),
        min_cluster=int(o.donor_id.value_counts().min()), max_cluster=int(o.donor_id.value_counts().max()),
        md5=hashlib.md5(open(p,"rb").read()).hexdigest(), dtypes={k:str(v) for k,v in o.dtypes.items()})
    print(name, info[name])
write(m, "ST", "ACS_STATES")
write(m[m.ST == 6], "PUMA", "ACS_CA_PUMA")
json.dump(info, open(f"{OUT}/conversion_info.json","w"), indent=1)
