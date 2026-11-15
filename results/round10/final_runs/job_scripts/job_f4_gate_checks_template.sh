#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=90
set -u
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=3f5eb01e-aa12-4f67-84ac-45c28e10831d
HJ=$PWD
OUT=$BASE/F4_gate/$UNIT
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
  "note": "F4 gate checks (provenance index over F1 to F4, numeric-claim sweep), unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
export PYTHONHASHSEED=0
REPORT=docs/round10/i05/final-runs/round10_final_runs_report.md
DEC=docs/round10/i05/final-runs/round10_final_runs_F3_decisions.md
CMD1="round10_final_runs_provenance_index.py $BASE $CLONE $COMMIT $OUT/provenance_index.csv F1,F2,F3,F4"
CMD2="verify_numeric_claims.py $REPORT $DEC --search-dir . --search-dir results/round10/final_runs/F4 --search-dir results/round10/final_runs/F4/aggregate --search-dir results/round10/final_runs/F3 --exceptions .verify-exceptions-round10-final-runs --tsv $OUT/verify_F4.tsv"
set +e
cd "$OUT"; $PY -u $SNAP/code/scripts/$CMD1 > index_stdout.log 2>&1; RC1=$?
cd "$CLONE"; git --no-optional-locks diff --quiet $COMMIT -- $REPORT $DEC .verify-exceptions-round10-final-runs; SAME=$?
$PY -u $SNAP/code/scripts/$CMD2 > "$OUT/verify_F4.txt" 2>&1; RC2=$?
set -e
echo "report and exceptions equal to $COMMIT: $([ $SAME -eq 0 ] && echo yes || echo no); index rc $RC1; verify rc $RC2" > "$OUT/gate_checks_summary.txt"
ST=COMPLETED; [ $RC1 -eq 0 ] || ST=FAILED_rc$RC1
cd "$OUT"
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F4 $UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD1; $CMD2" --config '{"stage":"F4","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_provenance_index.py code/scripts/verify_numeric_claims.py --inputs $CLONE/$REPORT $CLONE/$DEC $CLONE/.verify-exceptions-round10-final-runs
for g in PROVENANCE.txt _provenance.json index_stdout.log provenance_index.csv verify_F4.txt verify_F4.tsv gate_checks_summary.txt; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
cat gate_checks_summary.txt; tail -12 index_stdout.log; tail -80 verify_F4.txt
exit $RC1
