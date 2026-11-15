#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --time=90
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=10d578c5134bdcd9865639985c84933c71bade47
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F1/task_build_breast_ST
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
  "frame_id": "fc04d488-f9cc-4e63-99fc-f3a50dbc17ed",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F1.4c breast ST task definition by the corpus rule, with kidney anchor",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
mkdir -p "$OUT/inputs"

cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f1_task_build.py /work/users/w/e/weiyang/st_fed_learn/data breast "Spatial Transcriptomics" /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__breast__Spatial_Transcriptomics.csv $OUT > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F1 task_build_breast_ST $COMMIT $SNAP "$START" $ST --command "round10_final_runs_f1_task_build.py /work/users/w/e/weiyang/st_fed_learn/data breast 'Spatial Transcriptomics' /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__breast__Spatial_Transcriptomics.csv $OUT" --config '{"stage":"F1","unit":"task_build_breast_ST","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f1_task_build.py --inputs /work/users/w/e/weiyang/st_fed_learn/data/registry/samples.parquet /work/users/w/e/weiyang/st_fed_learn/data/tasks/kidney__Visium.json /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/audit_verdicts/donor_map__breast__Spatial_Transcriptomics.csv
cd "$OUT"; cp PROVENANCE.txt _provenance.json stdout.log "$HJ"/ 2>/dev/null; for g in *.json; do cp $g "$HJ"/ 2>/dev/null; done; true
tail -60 stdout.log
exit $RC
