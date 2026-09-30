
import os, sys, json, hashlib, datetime
import numpy as np
acs_dir, out_def, out_inv = sys.argv[1:4]
npz = os.path.join(acs_dir, "census_income.npz")
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
EXPECT = "9d49f41eaa4563dffaeec3ef8f354169"
assert md5(npz) == EXPECT, "npz md5 differs from the fetch-job record"
d = np.load(npz)
Y = d["Y"].astype(np.float64); Yh = d["Yhat"].astype(np.float64); X = d["X"]
n = len(Y)
age = X[:, 0].astype(float); sex = X[:, 1]
raw = json.load(open(os.path.join(acs_dir, "acs_fetch_raw.json")))
def r2(y, p):   # 1 - SSE/SST of p as a prediction of y (no refit)
    return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
def corr(a, b): return float(np.corrcoef(a, b)[0, 1])
tf = lambda v: np.log1p(np.clip(v, 0, None))
Ly, Lyh = tf(Y), tf(Yh)
stats = {
 "n_rows": int(n),
 "Y_eq_0": int((Y == 0).sum()), "Y_lt_0": int((Y < 0).sum()), "Y_le_0": int((Y <= 0).sum()),
 "Y_le_0_fraction": float((Y <= 0).mean()),
 "Y_min": float(Y.min()), "Yhat_le_0": int((Yh <= 0).sum()), "Yhat_lt_0": int((Yh < 0).sum()),
 "Yhat_min": float(Yh.min()),
 "age_min": float(age.min()), "age_max": float(age.max()), "age_mean": float(age.mean()), "age_sd_ddof0": float(age.std()),
 "age_lt_16": int((age < 16).sum()), "age_eq_0": int((age == 0).sum()),
 "sex_values": [int(v) for v in np.unique(sex)],
 "Y_le_0_among_age_lt_16": int(((Y <= 0) & (age < 16)).sum()),
}
pos = Y > 0
fit = {
 "unit_R2_raw_dollars_Yhat_as_prediction_of_Y": r2(Y, Yh),
 "unit_corr_raw_dollars": corr(Y, Yh),
 "unit_R2_log1p_clipped_all_rows": r2(Ly, Lyh),
 "unit_corr_log1p_clipped_all_rows": corr(Ly, Lyh),
 "unit_R2_log_Yhat_positive_only_rows_Y_gt_0_and_Yhat_gt_0": None,
 "cluster_level_R2": "not computable: no state or PUMA identifier in the package data",
}
m = (Y > 0) & (Yh > 0)
fit["n_rows_Y_gt_0_and_Yhat_gt_0"] = int(m.sum())
fit["unit_R2_log_Yhat_positive_only_rows_Y_gt_0_and_Yhat_gt_0"] = r2(np.log(Y[m]), np.log(Yh[m]))
fit["unit_corr_log_positive_only_rows"] = corr(np.log(Y[m]), np.log(Yh[m]))
# slope of log1p-clipped income on standardised age, full data (descriptive, not an estimand result)
z = (age - age.mean()) / age.std()
stats["descriptive_full_data_theta3_slope_log1p_income_on_z_age_Y"] = float(np.polyfit(z, Ly, 1)[0])
stats["descriptive_full_data_theta3_slope_log1p_income_on_z_age_Yhat"] = float(np.polyfit(z, Lyh, 1)[0])
stats["descriptive_full_data_mean_log1p_income_Y"] = float(Ly.mean())
stats["descriptive_full_data_mean_log1p_income_Yhat"] = float(Lyh.mean())
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
inv = {
 "inventory_version": 1, "dataset": "ppi_py census_income (ppi_python %s)" % "0.2.3",
 "file": "census_income.npz", "md5": EXPECT,
 "sha256": raw["files"]["census_income.npz"]["sha256"], "bytes": raw["files"]["census_income.npz"]["bytes"],
 "arrays": raw["inventory"]["arrays"], "npz_keys": raw["inventory"]["npz_keys"],
 "column_names_in_file": "none: X is an unnamed 2-column integer array; columns are read by position",
 "X_column_interpretation": {"X[:,0]": "age (inferred: integer 0 to 94, 92 distinct values)", "X[:,1]": "sex (inferred: values 1 and 2)", "basis": "value ranges; the npz carries no column labels; to be confirmed against ppi_py documentation"},
 "state_identifier_present": False, "puma_identifier_present": False, "survey_year_present": False,
 "yhat_present": True, "yhat_dtype": "float32",
 "yhat_origin": "gradient-boosted predictions shipped in the file (by the package description; training split not stated in the file)",
 "outcome_scale": "raw dollars (income), not log; Y ranges from -7200 to 1403700",
 "stats": stats, "predictor_fit": fit,
 "escalation": "state and PUMA identifiers and a survey year are absent from the package's census_income file. By the brief's hard limit no other source was fetched. The ACS cluster units (Q2, Q4 state and PUMA settings, the state-by-year two-way supplement) cannot run on this file as it stands.",
 "generated_at": now,
}
json.dump(inv, open(out_inv, "w"), indent=1)
td = {
 "task_def_version": 1,
 "task": "ACS_INCOME",
 "label_set": "package",
 "source": "ppi_py",
 "st_technology": "not applicable (tabular ACS PUMS survey microdata)",
 "repo_root_relative": True,
 "paths": {"data": "results/round4/ppi/Q0_setup/acs/census_income.npz", "data_md5": EXPECT,
           "arrays": {"Y": "income, raw dollars, float64", "Yhat": "package gradient-boosted prediction, raw dollars, float32", "X": "int64 (n, 2): age, sex (by position)"}},
 "adaptation_note": "A0 format adapted for tabular data: paths.adata/patches/embeddings and target_genes have no analogue and are replaced by paths.data and the outcome block; samples becomes clusters (the grouping units); the HEST donor folds are omitted (no folds are defined here; labelled-cluster subsets are drawn by the Q4 ACS unit).",
 "n_units": int(n),
 "clusters": {
   "level_1": {"name": "state", "field": None, "status": "absent", "n": None, "note": "no state identifier in the package file"},
   "level_2": {"name": "PUMA", "field": None, "status": "absent", "n": None, "nested_in": "state (by ACS definition)", "note": "no PUMA identifier in the package file"},
   "survey_year": {"field": None, "status": "absent", "note": "no year in the package file; state-by-year two-way clustering (Q4) cannot be done on this file"}
 },
 "outcome": {
   "name": "log income", "raw_array": "Y",
   "transform": "log1p of income clipped at zero: y_tilde = log(1 + max(Y, 0))",
   "transform_status": "PROPOSED by the ACS data unit; the brief says log of income and asks for a stated handling of zero and negative incomes, and this choice needs the lead's confirmation before Q2 or Q4 use it",
   "zero_or_negative_handling": "incomes at or below zero map to log(1)=0 instead of being dropped, because dropping rows by the outcome cannot be applied to the unlabelled rows (no Y there) and would change the estimand between L and U. The same map is applied to the predictor.",
   "n_income_eq_0": stats["Y_eq_0"], "n_income_lt_0": stats["Y_lt_0"], "n_income_le_0": stats["Y_le_0"], "fraction_income_le_0": stats["Y_le_0_fraction"],
   "alternative_not_chosen": "drop rows with Y <= 0 (a strict log); would remove the counts above and make the target population differ from the package's"
 },
 "covariates": {"theta_3": {"name": "age, standardised", "raw_array": "X[:,0]", "raw_column_status": "inferred to be age from value range; not labelled in the file",
                 "standardisation": "z = (age - mean) / sd over all %d rows, sd with ddof=0" % n, "age_mean": stats["age_mean"], "age_sd_ddof0": stats["age_sd_ddof0"]}},
 "estimands": {"theta_2": "mean of log income (spot-weighted and cluster-weighted as in plan section Q4)", "theta_3": "slope of log income on standardised age"},
 "predictor": {"source": "package gradient-boosted predictions (Yhat in the file)", "present": True, "fit_here": False,
               "map_to_outcome_scale": "log(1 + max(Yhat, 0)), the same map as the outcome", "n_Yhat_le_0": stats["Yhat_le_0"], "n_Yhat_lt_0": stats["Yhat_lt_0"],
               "unit_R2_on_outcome_scale_log1p_clipped": fit["unit_R2_log1p_clipped_all_rows"], "unit_corr_on_outcome_scale": fit["unit_corr_log1p_clipped_all_rows"],
               "unit_R2_raw_dollars": fit["unit_R2_raw_dollars_Yhat_as_prediction_of_Y"],
               "cluster_level_R2": fit["cluster_level_R2"],
               "training_split": "not recorded in the file; no held-out split was fitted here because Yhat is present"},
 "flags": {"cluster_fields_absent": True, "survey_year_absent": True, "escalation": inv["escalation"]},
 "provenance": {"generated_by": "acs_taskdef.py (staged in the job workdir; md5 recorded in PROVENANCE_taskdef.txt)", "generated_at": now, "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
                "inputs": ["results/round4/ppi/Q0_setup/acs/census_income.npz md5 " + EXPECT, "results/round4/ppi/Q0_setup/acs/acs_fetch_raw.json"]},
}
json.dump(td, open(out_def, "w"), indent=1)
print(json.dumps({"stats": stats, "fit": fit}, indent=1))
