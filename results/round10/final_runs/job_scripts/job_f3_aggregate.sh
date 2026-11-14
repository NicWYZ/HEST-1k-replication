#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=60
set -u
# F3 aggregate (plan 5d.8 step 5): round10_final_runs_f3_aggregate.py over the committed F3 item aggregates of
# COMMIT, extracted from the clone by git archive into the unit directory, so the inputs are exactly the committed ones.
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=2b764a2a-b65e-44dd-a6fc-d51f9f0964af
HJ=$PWD
OUT=$BASE/F3/aggregate_job/$UNIT
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
  "note": "F3 aggregate (plan 5d.8 step 5), unit $UNIT, commit $COMMIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
set +e
RC=0
mkdir -p committed && git -C "$CLONE" archive "$COMMIT" results/round10/final_runs/F3 | tar -x -C committed || RC=7
IN=$OUT/committed/results/round10/final_runs/F3
[ -d "$IN" ] || RC=7
(cd committed && find results -type f | sort | xargs md5sum) > committed_md5.txt
echo "committed files $(wc -l < committed_md5.txt)"
S=$SNAP/code/scripts
export PYTHONHASHSEED=0 PYTHONPATH=$S OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
if [ $RC -eq 0 ]; then
  $PY -u $S/round10_final_runs_f3_aggregate.py $IN $OUT/aggregate > stdout.log 2>&1
  RC=$?
fi
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
CMD="round10_final_runs_f3_aggregate.py $IN $OUT/aggregate (IN = git archive $COMMIT results/round10/final_runs/F3)"
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "aggregate_job/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"aggregate_job","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_aggregate.py --inputs $OUT/committed_md5.txt
set -e
cd "$OUT"
for g in PROVENANCE.txt _provenance.json stdout.log check_script.txt aggregate/f3_predictions.csv aggregate/f3_aggregate_manifest.json; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log 2>/dev/null; true
exit 0
