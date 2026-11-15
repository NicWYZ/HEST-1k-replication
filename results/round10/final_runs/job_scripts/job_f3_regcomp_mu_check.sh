#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --time=30
set -u
# F3 regcomp mu check: is regime B's mu (E3 kind mean over F2.load's spots) the donor mean over morphology-joined
# spots, while cluster_values_v1's mu is the all-spot donor mean? One population, CCRCC uni_v2 log1p.
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=b66915a6-d96c-42d1-b0b7-edb7f5bf423f
HJ=$PWD
OUT=$BASE/F3/regimeB/$UNIT
START=$(date -Iseconds)
mkdir -p "$BASE/_snapshots"
exec 9>"$BASE/_snapshots/.lock"; flock 9
if [ ! -d "$SNAP" ]; then
  mkdir -p "$SNAP.tmp" && git -C "$CLONE" archive "$COMMIT" code | tar -x -C "$SNAP.tmp"
  (cd "$SNAP.tmp" && find code -type f -name '*.py' | sort | xargs md5sum > MD5SUMS)
  chmod -R a-w "$SNAP.tmp" && mv "$SNAP.tmp" "$SNAP"
fi
flock -u 9
if [ -e "$OUT" ]; then echo "OUT exists: $OUT, refusing"; exit 3; fi
mkdir -p "$OUT"
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_8450e231133d",
  "frame_id": "$FRAME",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F3 regcomp mu estimand check, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2
CFG=$CLONE/results/round10/final_runs/F3/configs/regcomp/f3_regcomp__pk_CCRCC__uni_v2__log1p__p07.json
cat > check_mu.py <<'PYEOF'
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
PYEOF
$PY -u check_mu.py $CFG > stdout.log 2>&1; RC=$?
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "regimeB/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "check_mu.py (inline in the job script) on $CFG" --config '{"stage":"F3","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_regimeB.py code/scripts/round10_final_runs_f3_regcomp.py --inputs $CFG
for g in PROVENANCE.txt _provenance.json mu_check.json stdout.log check_mu.py; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -40 stdout.log
exit 0
