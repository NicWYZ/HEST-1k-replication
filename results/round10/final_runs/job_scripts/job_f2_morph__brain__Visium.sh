#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=180
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=e5dfd2f06b3249210f5231e8dfa0a15516b9ce2f
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F2/morphology/brain__Visium
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
  "note": "F2 option (b): CellViT spot features on the corpus patches, task brain__Visium",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
CMD="round10_final_runs_f2_morphology.py brain__Visium /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__brain__Visium.csv /work/users/w/e/weiyang/st_fed_learn/data/hest $OUT --cellvit-roots /work/users/w/e/weiyang/hest_replication/hest_ext /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/cellvit_seg /work/users/w/e/weiyang/hest_replication/bench_data --reference /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_v2_ext/KIDNEY_POP54_morph.parquet /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_ext/breast_xenium/morphology.parquet /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_ext/lung_xenium/morphology.parquet /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_ext/indiana_kidney/morphology.parquet --predictions /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__uni_v2/pred__brain__Visium__uni_v2__donor.parquet"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 morph__brain__Visium $COMMIT $SNAP "$START" $ST --frame 311f766a-9eaf-4808-9fe7-7f16ec282d07 --command "$CMD" --config '{"stage":"F2","unit":"morph__brain__Visium","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_morphology.py code/scripts/round4_data_morphology.py code/scripts/morphology_features.py --inputs /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__brain__Visium.csv /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__uni_v2/pred__brain__Visium__uni_v2__donor.parquet /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_v2_ext/KIDNEY_POP54_morph.parquet /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_ext/breast_xenium/morphology.parquet /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_ext/lung_xenium/morphology.parquet /work/users/w/e/weiyang/hest_replication/instrumentation/morphology_ext/indiana_kidney/morphology.parquet
cd "$OUT"; cp PROVENANCE.txt _provenance.json stdout.log "$HJ"/ 2>/dev/null; for g in *.json *.csv; do cp $g "$HJ"/ 2>/dev/null; done; true
tail -60 stdout.log
exit $RC
