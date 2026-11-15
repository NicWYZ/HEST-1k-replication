#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=20
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=cc603174c9f331b9b8b05bb709a2baf98879752a
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F2/scores_v1
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
  "frame_id": "311f766a-9eaf-4808-9fe7-7f16ec282d07",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F2 scores v1, P10.1 part 1 and FR2 to FR6",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
CMD="round10_final_runs_f2_scores.py /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/aggregate_v1 /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/ppi/E4b_rejective/e4b_grid.csv $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 scores_v1 $COMMIT $SNAP "$START" $ST --frame 311f766a-9eaf-4808-9fe7-7f16ec282d07 --command "$CMD" --config '{"stage":"F2","unit":"scores_v1","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_scores.py --inputs /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/aggregate_v1/f2_regimeA_summary.csv /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/aggregate_v1/f2_switch_rule.csv /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/aggregate_v1/f2_fix1_cost.csv /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/ppi/E4b_rejective/e4b_grid.csv
cd "$OUT"; cp PROVENANCE.txt _provenance.json stdout.log "$HJ"/ 2>/dev/null; for g in *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
