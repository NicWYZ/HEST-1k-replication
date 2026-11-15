#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=30
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F3/institution/anchor_pearson_smoke
START=$(date -Iseconds)
CLONE_CONF=/work/users/w/e/weiyang/hest_code/round10-final-runs/results/round10/final_runs/F3/configs/institution
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
  "frame_id": "b9c04725-eaea-4b47-8586-4ff29636ba08",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F3.2 anchor check 2 (center-design median Pearson, kidney Visium uni_v2) and smoke of one production cell",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
CMD="round10_final_runs_f3_institution.py anchor_pearson --pred /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__center.parquet --f1-predictions /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round10/final_runs/F1/aggregate/f1_predictions.csv --task kidney__Visium --encoder uni_v2 --out $OUT"
CMD2="round10_final_runs_f3_institution.py run --config $CLONE_CONF/smoke_kidney_uni_v2.json --out $OUT/smoke"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
if [ $RC -eq 0 ]; then
  T0=$(date +%s)
  $PY -u $SNAP/code/scripts/$CMD2 >> stdout.log 2>&1
  RC=$?
  echo "smoke_wall_seconds $(( $(date +%s) - T0 ))" >> stdout.log
  cp smoke/*.csv smoke/*.json . 2>/dev/null
fi
set -e
CMD="$CMD ; $CMD2"
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 anchor_pearson_smoke $COMMIT $SNAP "$START" $ST --frame b9c04725-eaea-4b47-8586-4ff29636ba08 --command "$CMD" --config '{"stage":"F3","unit":"anchor_pearson_smoke","commit":"'$COMMIT'","smoke_config":"results/round10/final_runs/F3/configs/institution/smoke_kidney_uni_v2.json"}' --scripts code/scripts/round10_final_runs_f3_institution.py code/scripts/round4_conf_c3.py code/scripts/round4_conf_sim.py code/scripts/round4_conf_io.py --inputs /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__center.parquet /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round10/final_runs/F1/aggregate/f1_predictions.csv /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round10/final_runs/F3/configs/institution/smoke_kidney_uni_v2.json
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
