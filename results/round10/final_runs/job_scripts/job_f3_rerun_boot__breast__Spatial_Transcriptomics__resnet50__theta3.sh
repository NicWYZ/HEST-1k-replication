#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=42
set -u
UNIT=breast__Spatial_Transcriptomics__resnet50__theta3
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=242aa416-6800-44ec-92d9-2550dbcf6db8
HJ=$PWD
OUT=$BASE/F3/reruns/boot/$UNIT
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
  "note": "F3 open point 3, bootstrap arms under hoptimus0 and resnet50, production part, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
CFG=f3_rerun_boot__$UNIT.json
cp "$CLONE/results/round10/final_runs/F3/configs/reruns/regimeA_boot/$CFG" "$OUT/$CFG"
F2U=$($PY -c "import json,sys,os;c=json.load(open(sys.argv[1]));print(os.path.basename(c['f2_regimeA_config'])[len('f2_regimeA__'):-5])" "$OUT/$CFG")
CV=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['cluster_values']))" "$OUT/$CFG")
CMD="round10_final_runs_f2_regimeA.py $OUT/$CFG $OUT; round10_final_runs_f3_reruns_boot_check.py $OUT/regimeA_cells.parquet $BASE/F2/regimeA/$F2U/regimeA_cells.parquet $OUT/check"
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f2_regimeA.py $OUT/$CFG $OUT > stdout.log 2>&1
RC=$?
$PY -u $SNAP/code/scripts/round10_final_runs_f3_reruns_boot_check.py $OUT/regimeA_cells.parquet $BASE/F2/regimeA/$F2U/regimeA_cells.parquet $OUT/check >> stdout.log 2>&1
R2=$?; [ $RC -eq 0 ] && RC=$R2
cp check/boot_check.json . 2>/dev/null
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 reruns__$UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"reruns","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_regimeA.py code/scripts/round10_final_runs_estimators.py code/scripts/round10_final_runs_f3_reruns_boot_check.py --inputs $OUT/$CFG $CV $BASE/F2/regimeA/$F2U/regimeA_cells.parquet
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
