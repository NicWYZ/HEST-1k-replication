#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=60
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=051fe05fb044a58980f93f2b6f055b2695a489d3
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F1/diag_corpus_tasks
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
  "note": "F1.4 D12 and D13 on every donor-design prediction file of the six corpus tasks; emb_out on kidney Visium uni_v2",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
ST=COMPLETED
run_one() {
  local name=$1; local f=$2; shift 2
  local S0=$(date -Iseconds)
  $PY -u $SNAP/code/scripts/round10_final_runs_f1_donor_diag.py "$f" "$name" "$OUT" "$@" > "stdout__$name.log" 2>&1; local rc=$?
  echo "$name rc=$rc start=$S0 end=$(date -Iseconds)" >> runs.txt
  [ $rc -eq 0 ] || ST=FAILED
}
set +e
run_one kidney__Visium__uni_v2 "$BASE/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__donor.parquet" --task /work/users/w/e/weiyang/st_fed_learn/data/tasks/kidney__Visium.json --encoder uni_v2
run_one kidney__Visium__hoptimus0 "$BASE/F1/predict/kidney__Visium__hoptimus0/pred__kidney__Visium__hoptimus0__donor.parquet"
run_one kidney__Visium__resnet50 "$BASE/F1/predict/kidney__Visium__resnet50/pred__kidney__Visium__resnet50__donor.parquet"
run_one bowel__Visium__uni_v2 "$BASE/F1/predict/bowel__Visium__uni_v2/pred__bowel__Visium__uni_v2__donor.parquet"
run_one bowel__Visium__hoptimus0 "$BASE/F1/predict/bowel__Visium__hoptimus0/pred__bowel__Visium__hoptimus0__donor.parquet"
run_one bowel__Visium__resnet50 "$BASE/F1/predict/bowel__Visium__resnet50/pred__bowel__Visium__resnet50__donor.parquet"
run_one brain__Visium__uni_v2 "$BASE/F1/predict/brain__Visium__uni_v2/pred__brain__Visium__uni_v2__donor.parquet"
run_one brain__Visium__hoptimus0 "$BASE/F1/predict/brain__Visium__hoptimus0/pred__brain__Visium__hoptimus0__donor.parquet"
run_one brain__Visium__resnet50 "$BASE/F1/predict/brain__Visium__resnet50/pred__brain__Visium__resnet50__donor.parquet"
run_one breast__Spatial_Transcriptomics__uni_v2 "$BASE/F1/predict/breast__Spatial_Transcriptomics__uni_v2/pred__breast__Spatial_Transcriptomics__uni_v2__donor.parquet"
run_one breast__Spatial_Transcriptomics__hoptimus0 "$BASE/F1/predict/breast__Spatial_Transcriptomics__hoptimus0/pred__breast__Spatial_Transcriptomics__hoptimus0__donor.parquet"
run_one breast__Spatial_Transcriptomics__resnet50 "$BASE/F1/predict/breast__Spatial_Transcriptomics__resnet50/pred__breast__Spatial_Transcriptomics__resnet50__donor.parquet"
run_one breast__Xenium__uni_v2 "$BASE/F1/predict/breast__Xenium__uni_v2/pred__breast__Xenium__uni_v2__donor.parquet"
run_one breast__Xenium__hoptimus0 "$BASE/F1/predict/breast__Xenium__hoptimus0/pred__breast__Xenium__hoptimus0__donor.parquet"
run_one breast__Xenium__resnet50 "$BASE/F1/predict/breast__Xenium__resnet50/pred__breast__Xenium__resnet50__donor.parquet"
run_one lung__Xenium__uni_v2 "$BASE/F1/predict/lung__Xenium__uni_v2/pred__lung__Xenium__uni_v2__donor.parquet"
run_one lung__Xenium__hoptimus0 "$BASE/F1/predict/lung__Xenium__hoptimus0/pred__lung__Xenium__hoptimus0__donor.parquet"
run_one lung__Xenium__resnet50 "$BASE/F1/predict/lung__Xenium__resnet50/pred__lung__Xenium__resnet50__donor.parquet"
set -e
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F1.4 diag_corpus_tasks $COMMIT $SNAP "$START" $ST --command "round10_final_runs_f1_donor_diag.py <F1/predict/<task>__<enc>/pred__<task>__<enc>__donor.parquet> <task>__<enc> $OUT [--task kidney__Visium.json --encoder uni_v2 for kidney__Visium__uni_v2], for 6 tasks x 3 encoders" --config '{"stage":"F1.4","unit":"diag_corpus_tasks","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f1_donor_diag.py --inputs $(ls $BASE/F1/predict/*/pred__*__donor.parquet | grep -v center_grouped) /work/users/w/e/weiyang/st_fed_learn/data/tasks/kidney__Visium.json
cp PROVENANCE.txt _provenance.json runs.txt "$HJ"/ 2>/dev/null; cp d12_lodo_r2_medians__*.csv d13_donor_diagnostics__*.csv "$HJ"/ 2>/dev/null; true
cat runs.txt
[ "$ST" = COMPLETED ]
