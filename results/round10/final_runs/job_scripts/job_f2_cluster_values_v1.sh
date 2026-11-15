#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=150
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=99de99986e3b8ec3bcf8e58c50f37835e9aedcf7
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F2/cluster_values_v1
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
  "note": "F2.0 donor-level cluster values, HEST, ACS and corpus (mu only on corpus), with round 9 anchors",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
git -C "$CLONE" show $COMMIT:results/round10/final_runs/F2/configs/f2_cluster_values_config.json > "$OUT/f2_cluster_values_config.json"
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
CMD="round10_final_runs_f2_cluster_values.py $OUT/f2_cluster_values_config.json $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 cluster_values_v1 $COMMIT $SNAP "$START" $ST --frame 311f766a-9eaf-4808-9fe7-7f16ec282d07 --command "$CMD" --config '{"stage":"F2","unit":"cluster_values_v1","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_cluster_values.py --inputs $OUT/f2_cluster_values_config.json /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__hoptimus0.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__resnet50.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC_merged__uni_v2.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC_merged__hoptimus0.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC_merged__resnet50.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__hoptimus0.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__resnet50.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__hoptimus0.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__resnet50.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions/ACS_STATES.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__hoptimus0/pred__kidney__Visium__hoptimus0__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__resnet50/pred__kidney__Visium__resnet50__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Spatial_Transcriptomics__uni_v2/pred__breast__Spatial_Transcriptomics__uni_v2__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Spatial_Transcriptomics__hoptimus0/pred__breast__Spatial_Transcriptomics__hoptimus0__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Spatial_Transcriptomics__resnet50/pred__breast__Spatial_Transcriptomics__resnet50__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/bowel__Visium__uni_v2/pred__bowel__Visium__uni_v2__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/bowel__Visium__hoptimus0/pred__bowel__Visium__hoptimus0__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/bowel__Visium__resnet50/pred__bowel__Visium__resnet50__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__uni_v2/pred__brain__Visium__uni_v2__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__hoptimus0/pred__brain__Visium__hoptimus0__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__resnet50/pred__brain__Visium__resnet50__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Xenium__uni_v2/pred__breast__Xenium__uni_v2__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Xenium__hoptimus0/pred__breast__Xenium__hoptimus0__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Xenium__resnet50/pred__breast__Xenium__resnet50__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/lung__Xenium__uni_v2/pred__lung__Xenium__uni_v2__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/lung__Xenium__hoptimus0/pred__lung__Xenium__hoptimus0__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/lung__Xenium__resnet50/pred__lung__Xenium__resnet50__donor.parquet /work/users/w/e/weiyang/hest_replication/results/round9/claude_science/C0_cluster_summaries/c0_cluster_summaries.csv.gz /work/users/w/e/weiyang/hest_replication/results/round9/claude_science/C2_normalized/c2_normalized_summaries.csv.gz
cd "$OUT"; cp PROVENANCE.txt _provenance.json stdout.log "$HJ"/ 2>/dev/null; for g in *.json *.csv; do cp $g "$HJ"/ 2>/dev/null; done; true
tail -60 stdout.log
exit $RC
