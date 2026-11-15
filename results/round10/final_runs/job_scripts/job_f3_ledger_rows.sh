#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=150
set -u
# F3 job-ledger rows: round10_final_runs_ledger_rows.py over every PROVENANCE file under BASE/F3, for the
# Slurm ids not yet in the committed job_ledger.csv.
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=b66915a6-d96c-42d1-b0b7-edb7f5bf423f
HJ=$PWD
OUT=$BASE/F3_ledger/$UNIT
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
  "note": "F3 job-ledger rows, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts
CMD="round10_final_runs_ledger_rows.py $CLONE $BASE/F3 F3 $OUT/f3_ledger_new_rows.csv"
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_ledger_rows.py $CLONE $BASE/F3 F3 $OUT/f3_ledger_new_rows.csv > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "F3_ledger/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_ledger_rows.py --inputs $CLONE/results/round10/final_runs/job_ledger.csv
for g in PROVENANCE.txt _provenance.json stdout.log f3_ledger_new_rows.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -5 stdout.log; wc -l f3_ledger_new_rows.csv 2>/dev/null
exit 0
