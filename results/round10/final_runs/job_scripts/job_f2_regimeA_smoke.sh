#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=60
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=dd25eb27c6addd06e3cb3c08dce70e2526ea0c9e
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F2/regimeA_smoke
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
  "note": "F2.1 regime A smoke test (CCRCC uni_v2, two genes, all arms) and the round 9 driver anchor",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
git -C "$CLONE" show $COMMIT:results/round10/final_runs/F2/configs/f2_regimeA_smoke.json > "$OUT/f2_regimeA_smoke.json"
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
CMD="round10_final_runs_f2_regimeA.py $OUT/f2_regimeA_smoke.json $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 regimeA_smoke $COMMIT $SNAP "$START" $ST --frame 311f766a-9eaf-4808-9fe7-7f16ec282d07 --command "$CMD" --config '{"stage":"F2","unit":"regimeA_smoke","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f2_regimeA.py --inputs $OUT/f2_regimeA_smoke.json /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/cluster_values_v1/cluster_values__CCRCC.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/cluster_values_v1/cluster_values__CCRCC_merged.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/cluster_values_v1/cluster_values__INDIANA_KIDNEY.parquet /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/cluster_values_v1/cluster_values__LUNG_XENIUM.parquet /work/users/w/e/weiyang/hest_replication/results/round9/fewcluster/williams/i34_williams_summary_hest.csv
cd "$OUT"; cp PROVENANCE.txt _provenance.json stdout.log "$HJ"/ 2>/dev/null; for g in *.json *.csv; do cp $g "$HJ"/ 2>/dev/null; done; true
tail -60 stdout.log
exit $RC
