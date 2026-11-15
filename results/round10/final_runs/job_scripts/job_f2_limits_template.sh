#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
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
OUT=$BASE/F2/limits/$UNIT
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
  "note": "F2.1 limits arms, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
CFG=f2_limits__$UNIT.json
git -C "$CLONE" show $COMMIT:results/round10/final_runs/F2/configs/limits/$CFG > "$OUT/$CFG"
INPUTS=$($PY -c "import json,sys;c=json.load(open(sys.argv[1]));a=c.get('anchor_r5') or {};print(' '.join(c['cluster_values']+[a[k] for k in ('pred_parquet','e4b_script','e4b_grid') if k in a]))" "$OUT/$CFG")
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
CMD="round10_final_runs_f2_limits.py $OUT/$CFG $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 limits__$UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F2","unit":"limits__'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_limits.py code/scripts/round10_final_runs_f2_regimeA.py code/scripts/round10_final_runs_estimators.py code/scripts/round4_ppi_estimator.py code/scripts/round5_ppi_estimator.py code/scripts/round5_ppi_balance.py code/scripts/round7_ppi_s2_comparators.py --inputs $OUT/$CFG $INPUTS
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -40 stdout.log
exit $RC
