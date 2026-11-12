#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=30
set -u
UNIT=prod_aggregate
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
  "note": "F3 open points 3 and 4, aggregation and scores of the production reruns, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
CMD="round10_final_runs_f2_aggregate.py $BASE/F3/reruns/boot $OUT/aggregate_boot; round10_final_runs_f2_limits_aggregate.py $BASE/F3/reruns/limits $CLONE/results/round10/final_runs/F2/aggregate $CLONE/results/round10/final_runs/F3/configs/reruns/limits $OUT/aggregate_limits_norm_refit; round10_final_runs_f3_reruns_prod_scores.py $CLONE $BASE $OUT; round10_final_runs_ledger_rows.py $CLONE $BASE/F3/reruns F3 $OUT/f3_reruns_ledger_new_rows.csv"
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f2_aggregate.py $BASE/F3/reruns/boot $OUT/aggregate_boot > stdout.log 2>&1
RC=$?
$PY -u $SNAP/code/scripts/round10_final_runs_f2_limits_aggregate.py $BASE/F3/reruns/limits $CLONE/results/round10/final_runs/F2/aggregate $CLONE/results/round10/final_runs/F3/configs/reruns/limits $OUT/aggregate_limits_norm_refit >> stdout.log 2>&1
R2=$?; [ $RC -eq 0 ] && RC=$R2
$PY -u $SNAP/code/scripts/round10_final_runs_f3_reruns_prod_scores.py $CLONE $BASE $OUT >> stdout.log 2>&1
R3=$?; [ $RC -eq 0 ] && RC=$R3
$PY -u $SNAP/code/scripts/round10_final_runs_ledger_rows.py $CLONE $BASE/F3/reruns F3 $OUT/f3_reruns_ledger_new_rows.csv >> stdout.log 2>&1
R4=$?; [ $RC -eq 0 ] && RC=$R4
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 reruns__$UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"reruns","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_aggregate.py code/scripts/round10_final_runs_f2_limits_aggregate.py code/scripts/round10_final_runs_f3_reruns_prod_scores.py code/scripts/round10_final_runs_ledger_rows.py --inputs $CLONE/results/round10/final_runs/F2/aggregate/f2_regimeA_summary.csv.gz $CLONE/results/round10/final_runs/F2/aggregate_limits/f2_limits_summary.csv $CLONE/results/round10/final_runs/job_ledger.csv
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
