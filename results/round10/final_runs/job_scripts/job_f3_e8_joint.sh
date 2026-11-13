#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=180
set -u
# F3 5d.4 items 2 to 5, E8 joint table: round10_final_runs_f3_e8_joint.py from the code snapshot of COMMIT. If STAGED
# is not "none", the staged script is overlaid on a copy of the snapshot's code/ (md5 checked against DRIVER_MD5),
# as job_f3_map_item7_check.sh does; the production run uses STAGED=none on the commit that carries the script.
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
STAGED=__STAGED_DRIVER__
DRIVER_MD5=__DRIVER_MD5__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=4ca471b7-8d08-41d9-a9df-67fff51f4222
HJ=$PWD
OUT=$BASE/F3/e8/$UNIT
MAPIN=$BASE/F3/map/map_aggregate/inputs.txt
ACS=$BASE/F3/map/acs_prod/acs_o_sweep.csv
MBT=$CLONE/results/round10/final_runs/F3/map/map_aggregate/map_by_task.csv
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
  "note": "F3 5d.4 items 2 to 5, E8 joint table (snapshot $COMMIT, staged overlay $STAGED md5 $DRIVER_MD5)",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
if [ "$STAGED" = "none" ]; then
  S=$SNAP/code/scripts
else
  mkdir -p overlay && cp -r "$SNAP/code" overlay/ && chmod -R u+w overlay
  cp "$STAGED" overlay/code/scripts/round10_final_runs_f3_e8_joint.py
  GOT=$(md5sum overlay/code/scripts/round10_final_runs_f3_e8_joint.py | cut -d' ' -f1)
  echo "driver_md5 $GOT expected $DRIVER_MD5" > check_driver.txt
  [ "$GOT" = "$DRIVER_MD5" ] || { echo "driver md5 mismatch"; echo 4 > rc_driver; }
  S=$OUT/overlay/code/scripts
fi
md5sum $MAPIN $ACS $MBT > inputs_md5.txt
export PYTHONHASHSEED=0 PYTHONPATH=$S OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
SCRIPTS="code/scripts/round10_final_runs_f3_e8_joint.py code/scripts/round5_conf_w3_merge.py code/scripts/round10_final_runs_f3_map_aggregate.py code/scripts/round4_conf_c3.py"
[ "$STAGED" = "none" ] || SCRIPTS="code/scripts/round5_conf_w3_merge.py code/scripts/round10_final_runs_f3_map_aggregate.py code/scripts/round4_conf_c3.py"
set +e
if [ ! -e rc_driver ]; then
  $PY -u $S/round10_final_runs_f3_e8_joint.py "$OUT/e8" --regb-root $BASE/F3/regimeB --map-inputs $MAPIN --acs $ACS --map-by-task $MBT --workers 8 > e8.log 2>&1; echo $? > rc_e8
  grep -q '"passed": true' e8/e8_checks.json || echo 6 > rc_spot
fi
RC=0
for f in rc_*; do [ -e "$f" ] || continue; v=$(cat "$f"); [ "$v" = "0" ] || RC=$v; done
ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "e8/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round10_final_runs_f3_e8_joint.py $OUT/e8 --regb-root $BASE/F3/regimeB --map-inputs $MAPIN --acs $ACS --map-by-task $MBT --workers 8 (scripts from $S; staged overlay $STAGED md5 $DRIVER_MD5)" --config '{"stage":"F3","track_dir":"e8","unit":"'$UNIT'","commit":"'$COMMIT'","driver_md5":"'$DRIVER_MD5'"}' --scripts $SCRIPTS --inputs $MAPIN $ACS $MBT $( [ "$STAGED" = "none" ] || echo $STAGED )
cd "$OUT"
for g in PROVENANCE.txt _provenance.json *.txt *.log rc_* e8/e8_checks.json; do [ -e "$g" ] && cp "$g" "$HJ"/; done
true
for g in *.log; do [ -e "$g" ] && echo "=== $g" && tail -8 "$g"; done
exit 0
