#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=20
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=5e381147f3b99e1087d874628be44b741814e3dc
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F1_gate/provenance_index_v2
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
  "note": "F1 gate provenance index",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_provenance_index.py $BASE $CLONE $COMMIT "$OUT/provenance_index.csv" > stdout.log 2>&1; RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F1 provenance_index $COMMIT $SNAP "$START" $ST --command "round10_final_runs_provenance_index.py $BASE $CLONE $COMMIT $OUT/provenance_index.csv" --config '{"stage":"F1","unit":"provenance_index","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_provenance_index.py --inputs $CLONE/.git/HEAD
cp PROVENANCE.txt _provenance.json stdout.log provenance_index.csv "$HJ"/ 2>/dev/null; true
cat stdout.log | tail -40
exit $RC
