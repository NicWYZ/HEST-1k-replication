#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=90
set -u
UNIT=smoke_scores2
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
B=/work/users/w/e/weiyang/hest_replication/results
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=73454d7a-85a3-4de7-9ee7-a74d0d999889
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
  "note": "F3.1 item 7 smoke rerun: adaptive scores in the map design, one cell timed per task",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
S=$SNAP/code/scripts
export PYTHONHASHSEED=0 PYTHONPATH=$S OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
M="$PY -u $S/round10_final_runs_f3_map.py"
set +e
( $M scores --task CCRCC:24 --encoder uni_v2 --folds INT1 --cal-draws 0 --cqr-genes 5 --out $OUT/scores_ccrcc > scores_ccrcc.log 2>&1; echo $? > rc_scores_ccrcc ) &
( $M scores --task LUNG_XENIUM --encoder uni_v2 --folds lungXen_THD0008 --cal-draws 0 --cqr-genes 3 --out $OUT/scores_lung > scores_lung.log 2>&1; echo $? > rc_scores_lung ) &
( $M scores --task INDIANA_KIDNEY --encoder uni_v2 --folds kidVis_atlas_21-015 --cal-draws 0 --cqr-genes 3 --out $OUT/scores_indiana > scores_indiana.log 2>&1; echo $? > rc_scores_indiana ) &
wait
RC=0
for f in rc_*; do [ -e "$f" ] || continue; v=$(cat "$f"); [ "$v" = "0" ] || RC=$v; done
ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $S/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round10_final_runs_f3_map.py scores smoke on CCRCC:24, LUNG_XENIUM, INDIANA_KIDNEY (uni_v2, one fold, cal draw 0)" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_map.py code/scripts/round10_final_runs_f3_map_anchor.py code/scripts/round10_final_runs_f3_map_aggregate.py code/scripts/round4_conf_c3.py code/scripts/round5_conf_w3.py code/scripts/round4_conf_io.py code/scripts/round4_conf_sim.py code/scripts/round5_conf_io.py code/scripts/round3_a0_harness.py code/scripts/round3_a4b_hcp.py code/scripts/round3_d4_sets.py code/scripts/round10_final_runs_f2_refit_norm.py code/scripts/round3_a4_scores.py --inputs $B/round3/task_defs/CCRCC.json
cd "$OUT"
for g in PROVENANCE.txt _provenance.json *.json *.csv rc_*; do [ -e "$g" ] && cp "$g" "$HJ"/; done
for g in */*.json */*timing*.csv */*by_fold*.csv */*summary*.csv */*compare*.csv */map_p103.csv; do [ -e "$g" ] && cp "$g" "$HJ"/"$(echo $g | tr / _)"; done
true
for g in *.log; do [ -e "$g" ] && echo "=== $g" && tail -8 "$g"; done
exit 0
