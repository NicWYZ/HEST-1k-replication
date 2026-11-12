#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=45
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F3/institution/production
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
  "frame_id": "b9c04725-eaea-4b47-8586-4ff29636ba08",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F3.2 institution axis production: 4 tasks x 3 encoders x 2 scales, hcp_center and hcp_donor",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
CMD="round10_final_runs_f3_institution.py run --config /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round10/final_runs/F3/configs/institution/production.json --out $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 production $COMMIT $SNAP "$START" $ST --frame b9c04725-eaea-4b47-8586-4ff29636ba08 --command "$CMD" --config '{"stage":"F3","unit":"production","commit":"'$COMMIT'","config":"results/round10/final_runs/F3/configs/institution/production.json"}' --scripts code/scripts/round10_final_runs_f3_institution.py code/scripts/round4_conf_c3.py code/scripts/round4_conf_sim.py code/scripts/round4_conf_io.py --inputs /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round10/final_runs/F3/configs/institution/production.json /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__hoptimus0/pred__kidney__Visium__hoptimus0__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/kidney__Visium__resnet50/pred__kidney__Visium__resnet50__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__hoptimus0/pred__brain__Visium__hoptimus0__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__uni_v2/pred__brain__Visium__uni_v2__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/brain__Visium__resnet50/pred__brain__Visium__resnet50__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/bowel__Visium__hoptimus0/pred__bowel__Visium__hoptimus0__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/bowel__Visium__uni_v2/pred__bowel__Visium__uni_v2__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/bowel__Visium__resnet50/pred__bowel__Visium__resnet50__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Xenium__hoptimus0__center_grouped/pred__breast__Xenium__hoptimus0__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Xenium__uni_v2__center_grouped/pred__breast__Xenium__uni_v2__center.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/predict/breast__Xenium__resnet50__center_grouped/pred__breast__Xenium__resnet50__center.parquet
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
