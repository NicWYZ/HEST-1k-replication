#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=30
set -u
UNIT=r9g42_diagcheck
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
  "note": "F3 open point 6, mechanism check of the all-gene diagnostics anchor, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
CFG=f2_diagnostics_v2.json
cp "$CLONE/results/round10/final_runs/F2/configs/$CFG" "$OUT/$CFG"
CMD="round10_final_runs_f2_diagnostics.py $OUT/$CFG $OUT/diag_full; round10_final_runs_f3_reruns_r9g42_diagcheck.py $CLONE $BASE/F3/reruns/r9g42 $OUT/diag_full $OUT"
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f2_diagnostics.py $OUT/$CFG $OUT/diag_full > stdout.log 2>&1
RC=$?
$PY -u $SNAP/code/scripts/round10_final_runs_f3_reruns_r9g42_diagcheck.py $CLONE $BASE/F3/reruns/r9g42 $OUT/diag_full $OUT >> stdout.log 2>&1
R2=$?; [ $RC -eq 0 ] && RC=$R2
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 reruns__$UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"reruns","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_diagnostics.py code/scripts/round9_fewcluster_hest_kappa.py code/scripts/round9_c0_diagnostics.py code/scripts/round10_final_runs_f3_reruns_r9g42_diagcheck.py --inputs $OUT/$CFG $CLONE/results/round10/final_runs/F2/diagnostics/f2_shortfall.csv $BASE/F3/reruns/r9g42/f3_r9g42_summary.json
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
