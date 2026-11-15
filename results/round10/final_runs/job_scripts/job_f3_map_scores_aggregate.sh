#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=60
set -u
# F3.1 item 7 summary: round10_final_runs_f3_map_scores_aggregate.py over the scores_full files of every
# COMPLETED i7_* unit under BASE/F3/map (the i7_lung_part units write CQR parts only and contribute no file).
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=b66915a6-d96c-42d1-b0b7-edb7f5bf423f
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
  "note": "F3.1 item 7 summary of the adaptive-score units, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
: > units.txt; : > inputs.txt
for d in $BASE/F3/map/i7_*; do
  [ -e "$d/PROVENANCE.txt" ] && grep -q '^status: COMPLETED' "$d/PROVENANCE.txt" || continue
  echo "$(basename $d)" >> units.txt
  for g in $d/s*/scores_full__*.csv.gz; do [ -e "$g" ] && echo "$g" >> inputs.txt; done
done
echo "units $(wc -l < units.txt) inputs $(wc -l < inputs.txt)"
CMD="round10_final_runs_f3_map_scores_aggregate.py $OUT/aggregate <the scores_full files listed in inputs.txt>"
set +e
$PY -u $SNAP/code/scripts/round10_final_runs_f3_map_scores_aggregate.py $OUT/aggregate $(cat inputs.txt) > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMD" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_map_scores_aggregate.py --inputs $OUT/inputs.txt
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log units.txt inputs.txt aggregate/*.json aggregate/*.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -40 stdout.log
exit 0
