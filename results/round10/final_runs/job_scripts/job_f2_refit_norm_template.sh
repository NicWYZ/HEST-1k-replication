#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=40
set -u
UNIT=__UNIT__
TASK=__TASK__
ENC=__ENC__
COMMITTED=__COMMITTED__
EXTRA=__EXTRA__
CV=__CV__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=e57d4a98-8078-4281-8c49-84c1df952f94
HJ=$PWD
OUT=$BASE/F2/refit_norm/$UNIT
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
  "note": "F2.0 step 3 refit on the normalised outcome, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
REL=results/round10/final_runs/F2/refit_norm/$UNIT
S=$SNAP/code/scripts/round10_final_runs_f2_refit_norm.py
set +e
mkdir -p as_is norm
(cd as_is && $PY -u $S refit $TASK $ENC as_is $REL/as_is $EXTRA > stdout.log 2>&1); RC1=$?
(cd norm && $PY -u $S refit $TASK $ENC norm $REL/norm $EXTRA > stdout.log 2>&1); RC2=$?
VT=$TASK
$PY -u $S compare $TASK $ENC $COMMITTED $OUT/as_is/b1_predictions__${VT}__$ENC.parquet $OUT/norm/b1_predictions__${VT}__$ENC.parquet $CV $OUT > stdout.log 2>&1; RC3=$?
set -e
RC=$(( RC1 != 0 ? RC1 : (RC2 != 0 ? RC2 : RC3) ))
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc${RC1}_${RC2}_${RC3}
CMD="round10_final_runs_f2_refit_norm.py refit $TASK $ENC as_is|norm $REL/<mode> $EXTRA; compare"
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 refit_norm__$UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F2","unit":"refit_norm__'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_refit_norm.py code/scripts/round3_b1_ppi.py code/scripts/round3_a0_harness.py code/scripts/round4_ppi_q2_indiana_predict_driver.py code/scripts/round4_ppi_q2_lung_predict_driver.py code/scripts/round4_ppi_data.py --inputs $COMMITTED $CV $( [ -f "$EXTRA" ] && echo $EXTRA )
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json; do [ -e "$g" ] && cp "$g" "$HJ"/; done; for g in as_is/stdout.log norm/stdout.log as_is/refit_info__as_is.json norm/refit_info__norm.json; do [ -e "$g" ] && cp "$g" "$HJ"/$(echo $g | tr '/' '_'); done; true
tail -30 stdout.log; tail -5 as_is/stdout.log norm/stdout.log
exit $RC
