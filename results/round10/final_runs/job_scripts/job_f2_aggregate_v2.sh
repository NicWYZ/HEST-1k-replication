#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=48G
#SBATCH --time=60
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=25619ba54b0e039bbbb4ca8ec9b2c241de904610
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/aggregate_v2
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
{"writer": "claude-science", "project_id": "proj_8450e231133d", "frame_id": "311f766a-9eaf-4808-9fe7-7f16ec282d07", "track": "final-runs",
 "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md", "note": "F2 aggregation v2 over 40 regime A units, then scores v2",
 "host": "$(hostname)", "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f2_aggregate.py $BASE/F2/regimeA $OUT > stdout.log 2>&1
RC=$?
[ $RC -eq 0 ] && $PY -u $SNAP/code/scripts/round10_final_runs_f2_scores.py $OUT /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/ppi/E4b_rejective/e4b_grid.csv $OUT >> stdout.log 2>&1
RC2=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] && [ $RC2 -eq 0 ] || ST=FAILED_rc$RC.$RC2
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 aggregate_v2 $COMMIT $SNAP "$START" $ST --frame 311f766a-9eaf-4808-9fe7-7f16ec282d07 --command "round10_final_runs_f2_aggregate.py $BASE/F2/regimeA $OUT; round10_final_runs_f2_scores.py $OUT /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/ppi/E4b_rejective/e4b_grid.csv $OUT" --config '{"stage":"F2","unit":"aggregate_v2","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_aggregate.py code/scripts/round10_final_runs_f2_scores.py --inputs /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/ppi/E4b_rejective/e4b_grid.csv
cp PROVENANCE.txt _provenance.json stdout.log "$HJ"/; for g in *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
exit $RC
