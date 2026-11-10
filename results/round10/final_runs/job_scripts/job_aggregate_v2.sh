#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=30
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=fd11092096b0abbbc8de401f70dbb153eb0c3541
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F1/aggregate_v2
R3=/work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet
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
  "frame_id": "862fd1a1-1068-44b1-a365-9bc7cae686fe",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F1 aggregates for the F1 report, second version (adds predictions, D12, kidney D13, task list)",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f1_aggregate.py $BASE "$OUT" --r3-ccrcc $R3 > stdout.log 2>&1; RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F1 aggregate_v2 $COMMIT $SNAP "$START" $ST --command "round10_final_runs_f1_aggregate.py $BASE $OUT --r3-ccrcc $R3" --config '{"stage":"F1","unit":"aggregate_v2","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f1_aggregate.py --inputs $R3 $BASE/F1/audit_verdicts/f1_audit_task_counts.csv
cp PROVENANCE.txt _provenance.json stdout.log *.csv *.txt "$HJ"/ 2>/dev/null; true
cat stdout.log | tail -40
exit $RC
