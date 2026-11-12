#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=90
set -u
UNIT=limits_smoke
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=242aa416-6800-44ec-92d9-2550dbcf6db8
HJ=$PWD
OUT=$BASE/F3/reruns/$UNIT
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
  "note": "F3 open point 4, limits arms on norm_refit: config builder byte check and smoke part CCRCC__uni_v2__norm_refit, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
SU=CCRCC__uni_v2__norm_refit
mkdir -p root committed
mkdir -p root/results/round10/final_runs/F2/configs && cp -r "$CLONE/results/round10/final_runs/F2/configs/regimeA" root/results/round10/final_runs/F2/configs/
mkdir -p committed/results/round10/final_runs/F2/configs && cp -r "$CLONE/results/round10/final_runs/F2/configs/limits" committed/results/round10/final_runs/F2/configs/
CMD="round10_final_runs_f2_limits_configs.py $OUT/root; cmp against the committed limits configs; round10_final_runs_f2_limits.py configs_new/f2_limits__$SU.json run"
(find f2cfg root committed -name '*.json' 2>/dev/null | sort | xargs md5sum) > input_configs_md5.txt
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f2_limits_configs.py $OUT/root > stdout.log 2>&1
RC=$?
BUILT=root/results/round10/final_runs/F2/configs/limits
COMM=committed/results/round10/final_runs/F2/configs/limits
echo "config,status" > limits_config_compare.csv
for f in $COMM/*.json; do b=$(basename $f); if [ ! -e "$BUILT/$b" ]; then echo "$b,missing_in_built" >> limits_config_compare.csv; elif cmp -s "$f" "$BUILT/$b"; then echo "$b,identical" >> limits_config_compare.csv; else echo "$b,DIFFERENT" >> limits_config_compare.csv; fi; done
mkdir -p configs_new
for f in $BUILT/*.json; do b=$(basename $f); if [ ! -e "$COMM/$b" ]; then echo "$b,new" >> limits_config_compare.csv; cp "$f" configs_new/; fi; done
NC=$(ls $COMM/*.json | wc -l); NI=$(grep -c ',identical$' limits_config_compare.csv); NN=$(grep -c ',new$' limits_config_compare.csv); ND=$(grep -c 'DIFFERENT\|missing_in_built' limits_config_compare.csv)
echo "committed $NC identical $NI new $NN different_or_missing $ND" >> stdout.log
(cd configs_new && md5sum *.json > ../configs_new_md5.txt)
[ $ND -eq 0 ] && [ $NI -eq $NC ] || { echo "BYTE CHECK FAILED" >> stdout.log; RC=4; }
if [ $RC -eq 0 ]; then
  T0=$(date +%s)
  $PY -u $SNAP/code/scripts/round10_final_runs_f2_limits.py configs_new/f2_limits__$SU.json run >> stdout.log 2>&1
  RC=$?
  echo "limits wall seconds: $(( $(date +%s) - T0 ))" >> stdout.log
  cp run/limits_summary.json . 2>/dev/null
fi
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 reruns__$UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"reruns","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_limits_configs.py code/scripts/round10_final_runs_f2_limits.py code/scripts/round10_final_runs_f2_regimeA.py code/scripts/round10_final_runs_estimators.py code/scripts/round4_ppi_estimator.py code/scripts/round5_ppi_estimator.py code/scripts/round5_ppi_balance.py code/scripts/round7_ppi_s2_comparators.py --inputs $OUT/configs_new/f2_limits__$SU.json $BASE/F2/cluster_values_v3_refit/cluster_values__CCRCC.parquet
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv *.txt; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
