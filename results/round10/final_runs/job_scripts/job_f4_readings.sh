#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --time=60
set -u
# F4 readings (plan 5e.2 and 5e.3). __CODE_COMMIT__ is substituted at submission.
UNIT=readings_v1
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=bdb361de-6630-44e8-b0f8-8bd63dae9ad3
HJ=$PWD
OUT=$BASE/F4/readings/$UNIT
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
mkdir -p "$OUT/s0006" "$OUT/acs"
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_8450e231133d",
  "frame_id": "$FRAME",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F4 readings (plan 5e.2, 5e.3), unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2
ICFG=$CLONE/results/round10/final_runs/F3/configs/institution/production.json
IDX=$CLONE/results/round10/final_runs/F3/configs/regimeB/f3_production_index.json
T10=$CLONE/results/round10/final_runs/F3/aggregate/t10_regcomp_comparisons.csv
$PY -u $SNAP/code/scripts/round10_final_runs_f4_readings.py s0006 $ICFG "$OUT/s0006" > stdout.log 2>&1; RC1=$?
$PY -u $SNAP/code/scripts/round10_final_runs_f4_readings.py acs $IDX $BASE/F3/regimeB $T10 "$OUT/acs" >> stdout.log 2>&1; RC2=$?
ST=COMPLETED; [ $RC1 -eq 0 ] && [ $RC2 -eq 0 ] || ST=FAILED_rc$RC1$RC2
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F4 "readings/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round10_final_runs_f4_readings.py s0006 $ICFG; acs $IDX $BASE/F3/regimeB $T10" --config '{"stage":"F4","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f4_readings.py --inputs $ICFG $IDX $T10
for g in PROVENANCE.txt stdout.log s0006/*.json s0006/*.csv acs/*.json acs/*.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -40 stdout.log
exit 0
