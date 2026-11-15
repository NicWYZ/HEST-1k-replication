#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --time=90
set -u
UNIT=anchor_scores_smoke
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
  "note": "F3.1 anchor 3 (round3_a4_scores unchanged, CCRCC uni_v2) and adaptive-score smoke timing",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
S=$SNAP/code/scripts
export PYTHONHASHSEED=0 PYTHONPATH=$S OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
M="$PY -u $S/round10_final_runs_f3_map.py"
set +e
( OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 $PY -u $S/round3_a4_scores.py uni_v2 --task-def $B/round3/task_defs/CCRCC.json --designs random,patient,donor --scores abs,scaled,scaled_clip --alpha 0.10 --alpha-grid 0.02,0.05,0.075,0.10,0.15,0.20,0.30 --nb-genes 12 --nb-solver newton-cholesky --nb-tol 1e-6 --cqr-genes 6 --cqr-max-draws 1 --cqr-mark-only 1 --accept-tag main --out-dir results/round10/final_runs/F3/map/$UNIT/a4 --tag __f3anchor > a4.log 2>&1; echo $? > rc_a4 ) &
( $M scores --task CCRCC:24 --encoder uni_v2 --folds INT1 --cal-draws 0 --cqr-genes 5 --out $OUT/scores > scores.log 2>&1; echo $? > rc_scores ) &
( $M scores --task LUNG_XENIUM --encoder uni_v2 --cal-draws 0 --cqr-genes 3 --folds lungXen_THD0008 --out $OUT/scores_lung > scores_lung.log 2>&1; echo $? > rc_scores_lung ) &
wait
[ "$(cat rc_a4)" = "5" ] && echo "a4 acceptance exit 5 recorded; the anchor is read from anchor_a4.json" > a4_exit5.txt && echo 0 > rc_a4
$PY -u $S/round10_final_runs_f3_map_anchor.py a4 $OUT/a4/a4_scores_by_task__uni_v2__f3anchor.csv $B/round3/A4_scores/a4_scores_by_task__uni_v2__mainCCRCC.csv $OUT > anchor_a4.log 2>&1; echo $? > rc_anchor
RC=0
for f in rc_*; do [ -e "$f" ] || continue; v=$(cat "$f"); [ "$v" = "0" ] || RC=$v; done
ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $S/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round3_a4_scores.py (CCRCC, three designs, abs scaled scaled_clip) and round10_final_runs_f3_map.py scores smoke (see logs)" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_map.py code/scripts/round10_final_runs_f3_map_anchor.py code/scripts/round10_final_runs_f3_map_aggregate.py code/scripts/round4_conf_c3.py code/scripts/round5_conf_w3.py code/scripts/round4_conf_io.py code/scripts/round4_conf_sim.py code/scripts/round5_conf_io.py code/scripts/round3_a0_harness.py code/scripts/round3_a4b_hcp.py code/scripts/round3_d4_sets.py code/scripts/round10_final_runs_f2_refit_norm.py code/scripts/round3_a4_scores.py --inputs $B/round3/task_defs/CCRCC.json $B/round3/A4_scores/a4_scores_by_task__uni_v2__mainCCRCC.csv
cd "$OUT"
for g in PROVENANCE.txt _provenance.json *.json *.csv rc_*; do [ -e "$g" ] && cp "$g" "$HJ"/; done
for g in */*.json */*timing*.csv */*by_fold*.csv */*summary*.csv */*compare*.csv */map_p103.csv; do [ -e "$g" ] && cp "$g" "$HJ"/"$(echo $g | tr / _)"; done
true
for g in *.log; do [ -e "$g" ] && echo "=== $g" && tail -8 "$g"; done
exit 0
