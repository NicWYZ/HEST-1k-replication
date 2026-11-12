#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --time=90
set -u
UNIT=anchor_w3_smoke
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
  "note": "F3.1 anchor 1 (W3 part 1 unchanged, CCRCC:24 uni_v2, INT1 and INT5) and map smoke timing",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
S=$SNAP/code/scripts
export PYTHONHASHSEED=0 PYTHONPATH=$S OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
M="$PY -u $S/round10_final_runs_f3_map.py"
set +e
( $PY -u $S/round5_conf_w3.py --task CCRCC:24 --part 1 --encoders uni_v2 --folds INT1,INT5 --out $OUT/w3 > w3.log 2>&1; echo $? > rc_w3 ) &
( $M map --task CCRCC:24 --encoder uni_v2 --part 1 --folds INT1 --out $OUT/map_p1 > map_p1.log 2>&1; echo $? > rc_map_p1 ) &
( r=0; for t in CCRCC:24 INDIANA_KIDNEY LUNG_XENIUM; do f=first; [ "$t" = "CCRCC:24" ] && f=INT1; $M checkfit --task $t --encoder uni_v2 --fold $f --out $OUT/checkfit >> checkfit.log 2>&1 || r=$?; done; echo $r > rc_checkfit
  $M map --task CCRCC:24 --encoder uni_v2 --part 2 --K 20 --max-specs 1 --out $OUT/map_p2_K20 > map_p2.log 2>&1; echo $? > rc_map_p2 ) &
( $M map --task LUNG_XENIUM --encoder uni_v2 --part 1 --max-specs 1 --out $OUT/map_p1_lung > map_p1_lung.log 2>&1; echo $? > rc_map_p1_lung
  $M map --task INDIANA_KIDNEY --encoder uni_v2 --part 1 --max-specs 1 --out $OUT/map_p1_indiana > map_p1_indiana.log 2>&1; echo $? > rc_map_p1_indiana ) &
wait
$PY -u $S/round10_final_runs_f3_map_anchor.py w3 $OUT/w3 $CLONE/results/round5/conformal/W3_real/merged/w3_by_fold.csv $OUT --driver $OUT/map_p1/map_by_fold__CCRCC_24__uni_v2__p1.csv > anchor_w3.log 2>&1; echo $? > rc_anchor
$PY -u $S/round10_final_runs_f3_map_aggregate.py $OUT/agg_test $OUT/map_p1/map_full__CCRCC_24__uni_v2__p1.csv.gz > agg_test.log 2>&1; echo $? > rc_agg_test
RC=0
for f in rc_*; do [ -e "$f" ] || continue; v=$(cat "$f"); [ "$v" = "0" ] || RC=$v; done
ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $S/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round5_conf_w3.py --task CCRCC:24 --part 1 --encoders uni_v2 --folds INT1,INT5; round10_final_runs_f3_map.py map and checkfit smoke (see logs)" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_map.py code/scripts/round10_final_runs_f3_map_anchor.py code/scripts/round10_final_runs_f3_map_aggregate.py code/scripts/round4_conf_c3.py code/scripts/round5_conf_w3.py code/scripts/round4_conf_io.py code/scripts/round4_conf_sim.py code/scripts/round5_conf_io.py code/scripts/round3_a0_harness.py code/scripts/round3_a4b_hcp.py code/scripts/round3_d4_sets.py code/scripts/round10_final_runs_f2_refit_norm.py --inputs $CLONE/results/round5/conformal/W3_real/merged/w3_by_fold.csv $B/round3/task_defs/CCRCC.json $B/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet $BASE/F2/refit_norm/CCRCC__uni_v2/norm/b1_predictions__CCRCC__uni_v2.parquet
cd "$OUT"
for g in PROVENANCE.txt _provenance.json *.json *.csv rc_*; do [ -e "$g" ] && cp "$g" "$HJ"/; done
for g in */*.json */*timing*.csv */*by_fold*.csv */*summary*.csv */*compare*.csv */map_p103.csv; do [ -e "$g" ] && cp "$g" "$HJ"/"$(echo $g | tr / _)"; done
true
for g in *.log; do [ -e "$g" ] && echo "=== $g" && tail -8 "$g"; done
exit 0
