#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=60
set -u
UNIT=r9g42
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
  "note": "F3 open point 6, LUNG_XENIUM on round 9's 42-gene subset, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
CMD="round10_final_runs_f3_reruns_r9g42.py $CLONE $BASE $SNAP/code/scripts $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
INPUTS="$(ls $BASE/F2/regimeA/LUNG_XENIUM__*/regimeA_cells.parquet $BASE/F2/limits/LUNG_XENIUM__*/limits_cells.parquet $BASE/F2/limits/LUNG_XENIUM__*/limits_diag.parquet $BASE/F2/regimeB/LUNG_XENIUM__*/regimeB_genes.parquet $BASE/F2/cluster_values_v1/cluster_values__LUNG_XENIUM.parquet $BASE/F2/cluster_values_v3_refit/cluster_values__LUNG_XENIUM.parquet | tr '\n' ' ')"
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 reruns__$UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"reruns","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_reruns_r9g42.py code/scripts/round10_final_runs_f2_aggregate.py code/scripts/round10_final_runs_f2_limits_aggregate.py code/scripts/round10_final_runs_f2_regimeB_aggregate.py code/scripts/round10_final_runs_f2_diagnostics.py code/scripts/round9_fewcluster_hest_kappa.py code/scripts/round9_c0_diagnostics.py code/scripts/round10_final_runs_f2_scores.py --inputs $CLONE/results/round10/final_runs/F2/configs/f2_diagnostics_v2.json $CLONE/results/round10/final_runs/F2/aggregate/f2_units.csv $CLONE/results/round10/final_runs/F2/aggregate/f2_scores.csv $CLONE/results/round5/ppi/E4b_rejective/e4b_grid.csv $INPUTS
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
