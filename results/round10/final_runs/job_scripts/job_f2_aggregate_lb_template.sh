#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --time=40
set -u
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=e57d4a98-8078-4281-8c49-84c1df952f94
HJ=$PWD
OUT=$BASE/F2/$UNIT
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
  "note": "F2 aggregation of limits and regime B, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p cfg && git -C "$CLONE" archive $COMMIT results/round10/final_runs/F2/configs | tar -x -C cfg
CF=$OUT/cfg/results/round10/final_runs/F2/configs
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f2_limits_aggregate.py $BASE/F2/limits $BASE/F2/aggregate_v2 $CF/limits $OUT/limits > stdout_limits.log 2>&1; RC1=$?
$PY -u $SNAP/code/scripts/round10_final_runs_f2_regimeB_aggregate.py $BASE/F2/regimeB $CF/regimeB $OUT/regimeB > stdout_regimeB.log 2>&1; RC2=$?
set -e
RC=$(( RC1 != 0 ? RC1 : RC2 ))
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc${RC1}_${RC2}
CMD="round10_final_runs_f2_limits_aggregate.py F2/limits F2/aggregate_v2 configs/limits limits; round10_final_runs_f2_regimeB_aggregate.py F2/regimeB configs/regimeB regimeB"
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 $UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F2","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_limits_aggregate.py code/scripts/round10_final_runs_f2_regimeB_aggregate.py --inputs $BASE/F2/aggregate_v2/f2_regimeA_summary.csv
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout_limits.log stdout_regimeB.log limits/*.json limits/*.csv regimeB/*.json regimeB/*.csv; do [ -e "$g" ] && cp "$g" "$HJ"/$(echo $g | tr '/' '_'); done; true
tail -n 30 stdout_limits.log || true; tail -n 20 stdout_regimeB.log || true
exit $RC
