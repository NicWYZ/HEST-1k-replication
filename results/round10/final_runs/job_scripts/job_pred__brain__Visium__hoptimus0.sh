#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=240
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=3f99228ef9ede63650531774b4c0c34a8c7cd549
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F1/predict/brain__Visium__hoptimus0
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
  "frame_id": "fc04d488-f9cc-4e63-99fc-f3a50dbc17ed",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F1.4c held-out prediction files brain__Visium hoptimus0",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
set +e
S0=$(date -Iseconds)
$PY -u $SNAP/code/scripts/round10_final_runs_f1_predict.py /work/users/w/e/weiyang/st_fed_learn/data/tasks/brain__Visium.json hoptimus0 donor /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__brain__Visium.csv "$OUT" --only-mapped > stdout_donor.log 2>&1; RC_donor=$?
echo "donor rc=$RC_donor start=$S0 end=$(date -Iseconds)" >> runs.txt
S0=$(date -Iseconds)
$PY -u $SNAP/code/scripts/round10_final_runs_f1_predict.py /work/users/w/e/weiyang/st_fed_learn/data/tasks/brain__Visium.json hoptimus0 center /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__brain__Visium.csv "$OUT" --only-mapped > stdout_center.log 2>&1; RC_center=$?
echo "center rc=$RC_center start=$S0 end=$(date -Iseconds)" >> runs.txt
set -e
ST=COMPLETED; for r in $RC_donor $RC_center; do [ $r -eq 0 ] || ST=FAILED; done
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F1.4c brain__Visium__hoptimus0 $COMMIT $SNAP "$START" $ST --command "round10_final_runs_f1_predict.py /work/users/w/e/weiyang/st_fed_learn/data/tasks/brain__Visium.json hoptimus0 donor|center /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__brain__Visium.csv $OUT --only-mapped" --config '{"stage":"F1.4c","unit":"brain__Visium__hoptimus0","commit":"'$COMMIT'","designs":"donor|center"}' --scripts code/scripts/round10_final_runs_f1_predict.py code/scripts/round3_a0_harness.py --inputs /work/users/w/e/weiyang/st_fed_learn/data/tasks/brain__Visium.json /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__brain__Visium.csv
cp PROVENANCE.txt _provenance.json runs.txt stdout_*.log pred_summary__*.json "$HJ"/ 2>/dev/null; true
cat runs.txt; for f in stdout_*.log; do tail -3 $f; done
[ "$ST" = COMPLETED ]
