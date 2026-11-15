import json, sys
import numpy as np, pandas as pd
import round10_final_runs_f2_regimeB as F2
import round10_final_runs_f3_regcomp as RC
cfg = json.load(open(sys.argv[1])); pop = dict(cfg["populations"][0])
out = {"population": {k: pop[k] for k in ("task", "encoder", "scale", "parquet", "cluster_values", "theta2_kind")}}
data = F2.load(pop)
out["data_keys"] = sorted(data.keys())
Tset = RC.E3.build(data, pop["vtag"], pop.get("arm", pop["encoder"]))
out["Tset_keys"] = {k: (v.get("kind") if isinstance(v, dict) else str(type(v))) for k, v in Tset.items()}
T = next(v for v in Tset.values() if isinstance(v, dict) and v.get("kind") == "mean")
donors = [str(d) for d in data["donors"]]; genes = list(data["genes"])
zb = np.asarray(T["zbar"], float)
didx = np.asarray(data["didx"]); Y = np.asarray(data["Y"], float)
jmean = np.vstack([Y[didx == g].mean(0) for g in range(len(donors))])
out["n_spots_loaded"] = int(len(didx))
out["zbar_vs_loaded_donor_mean_max_abs"] = float(np.nanmax(np.abs(zb - jmean)))
cv = pd.read_parquet(pop["cluster_values"])
cv = cv[(cv.task == pop["task"]) & (cv.encoder == pop["encoder"]) & (cv.scale == pop["scale"]) & (cv.estimand == "mu")]
Z = cv.pivot(index="donor", columns="gene", values="z").loc[donors, genes].to_numpy(float)
out["zbar_vs_cluster_values_max_abs"] = float(np.nanmax(np.abs(zb - Z)))
out["zbar_vs_cluster_values_max_rel"] = float(np.nanmax(np.abs(zb - Z) / np.maximum(1e-12, np.abs(Z))))
raw = pd.read_parquet(pop["parquet"])
out["raw_columns_sample"] = [c for c in raw.columns if not c.startswith(("y_", "f_", "pred_", "Y_", "P_"))][:40]
out["raw_rows"] = int(len(raw))
dcol = next((c for c in ("donor", "donor_id", "patient", "cluster") if c in raw.columns), None)
ycols = [c for c in raw.columns if c.endswith(tuple(genes)) and c[: -len(c.split("_")[-1])] != ""]
out["donor_col"] = dcol
if dcol is not None:
    pre = None
    for p in ("y_", "Y_", "obs_", "true_"):
        if all((p + g) in raw.columns for g in genes):
            pre = p; break
    out["y_prefix"] = pre
    if pre is not None:
        A = raw.groupby(raw[dcol].astype(str))[[pre + g for g in genes]].mean().loc[donors].to_numpy(float)
        out["allspot_mean_vs_cluster_values_max_abs"] = float(np.nanmax(np.abs(A - Z)))
        out["allspot_mean_vs_zbar_max_abs"] = float(np.nanmax(np.abs(A - zb)))
        cnt = raw.groupby(raw[dcol].astype(str)).size().loc[donors].to_numpy()
        ld = np.bincount(didx, minlength=len(donors))
        out["join_rate_by_donor"] = {d: round(float(l) / float(c), 4) for d, l, c in zip(donors, ld, cnt)}
        dd = np.nanmax(np.abs(zb - Z), axis=1)
        out["per_donor_max_abs_diff"] = {d: float(v) for d, v in zip(donors, dd)}
json.dump(out, open("mu_check.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("join_rate_by_donor", "per_donor_max_abs_diff")}, indent=1))
