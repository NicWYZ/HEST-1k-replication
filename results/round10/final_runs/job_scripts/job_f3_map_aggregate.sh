#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=128G
#SBATCH --time=240
set -u
UNIT=map_aggregate
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=cfa6989718a0ee78c79323454f452b855631d9eb
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=09de02c2-2098-4389-8ef9-287a670134b1
HJ=$PWD
OUT=$BASE/F3/map/$UNIT
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
  "note": "F3.1 map aggregation (tables, bootstrap SEs, P10.3) over the map grid units p1_*, p2_*, p2s_*, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
ls -1 $BASE/F3/map/p1_*/s*/map_full__*.csv.gz $BASE/F3/map/p2_*/s*/map_full__*.csv.gz $BASE/F3/map/p2s_*/s*/map_full__*.csv.gz > inputs.txt
echo "n_inputs $(wc -l < inputs.txt)"
CMD="round10_final_runs_f3_map_aggregate.py $OUT/aggregate <the map_full__*.csv.gz of BASE/F3/map/p1_*, p2_*, p2s_* listed in inputs.txt>"
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f3_map_aggregate.py $OUT/aggregate $(cat inputs.txt) > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_map_aggregate.py --inputs $OUT/inputs.txt
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log inputs.txt aggregate/*.json aggregate/*.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
