#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=120
set -u
# Pre-commit check of the CQR gene-range option: code snapshot of COMMIT with the edited driver overlaid from
# STAGED (md5 checked). (a) round 3's A4 anchor rerun and a default scores run against smoke_scores2's rows;
# (b) CCRCC:24 INT1 cal 0 unsharded vs three gene-range parts merged with --cqr-from; LUNG 43-gene part timed.
UNIT=item7_check
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
B=/work/users/w/e/weiyang/hest_replication/results
COMMIT=__CODE_COMMIT__
STAGED=__STAGED_DRIVER__
DRIVER_MD5=__DRIVER_MD5__
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
  "note": "F3.1 item 7 pre-commit check of the CQR gene-range option (driver overlay md5 $DRIVER_MD5 on snapshot $COMMIT)",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
mkdir -p overlay && cp -r "$SNAP/code" overlay/ && chmod -R u+w overlay
cp "$STAGED" overlay/code/scripts/round10_final_runs_f3_map.py
GOT=$(md5sum overlay/code/scripts/round10_final_runs_f3_map.py | cut -d' ' -f1)
echo "driver_md5 $GOT expected $DRIVER_MD5" > check_driver.txt
[ "$GOT" = "$DRIVER_MD5" ] || { echo "driver md5 mismatch"; echo 4 > rc_driver; }
S=$OUT/overlay/code/scripts
export PYTHONHASHSEED=0 PYTHONPATH=$S OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
M="$PY -u $S/round10_final_runs_f3_map.py"
CC="--task CCRCC:24 --encoder uni_v2 --folds INT1 --cal-draws 0"
set +e
( OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 $PY -u $S/round3_a4_scores.py uni_v2 --task-def $B/round3/task_defs/CCRCC.json --designs random,patient,donor --scores abs,scaled,scaled_clip --alpha 0.10 --alpha-grid 0.02,0.05,0.075,0.10,0.15,0.20,0.30 --nb-genes 12 --nb-solver newton-cholesky --nb-tol 1e-6 --cqr-genes 6 --cqr-max-draws 1 --cqr-mark-only 1 --accept-tag main --out-dir $OUT/a4 --tag __f3anchor > a4.log 2>&1; echo $? > rc_a4
  [ "$(cat rc_a4)" = "5" ] && echo "a4 acceptance exit 5 recorded; the anchor is read from anchor_a4.json" > a4_exit5.txt && echo 0 > rc_a4
  $PY -u $S/round10_final_runs_f3_map_anchor.py a4 $OUT/a4/a4_scores_by_task__uni_v2__f3anchor.csv $B/round3/A4_scores/a4_scores_by_task__uni_v2__mainCCRCC.csv $OUT > anchor_a4.log 2>&1; echo $? > rc_anchor ) &
( $M scores $CC --cqr-genes 5 --out $OUT/default5 > default5.log 2>&1; echo $? > rc_default5
  $M scores $CC --cqr-gene-range 0:17 --out $OUT/part_a > part_a.log 2>&1; echo $? > rc_part_a ) &
PA=$!
( $M scores $CC --out $OUT/unsharded > unsharded.log 2>&1; echo $? > rc_unsharded ) &
( $M scores $CC --cqr-gene-range 17:34 --out $OUT/part_b > part_b.log 2>&1; echo $? > rc_part_b ) &
PB=$!
( $M scores $CC --cqr-gene-range 34:50 --out $OUT/part_c > part_c.log 2>&1; echo $? > rc_part_c ) &
PC=$!
( $M scores --task LUNG_XENIUM --encoder uni_v2 --folds lungXen_THD0008 --cal-draws 0 --cqr-gene-range 0:43 --out $OUT/lung_part0 > lung_part0.log 2>&1; echo $? > rc_lung_part0 ) &
wait $PA $PB $PC
( $M scores $CC --cqr-from $OUT/part_a,$OUT/part_b,$OUT/part_c --out $OUT/merged > merged.log 2>&1; echo $? > rc_merged ) &
wait
{
  R=$BASE/F3/map/smoke_scores2/scores_ccrcc
  N=scores_full__CCRCC_24__uni_v2.csv.gz; BF=scores_by_fold__CCRCC_24__uni_v2.csv
  zcat $OUT/default5/$N > t_default5.csv; zcat $R/$N > t_smoke.csv
  zcat $OUT/merged/$N > t_merged.csv; zcat $OUT/unsharded/$N > t_unsharded.csv
  echo "default5_vs_smoke_scores2 rows $(wc -l < t_default5.csv) $(wc -l < t_smoke.csv)"
  cmp t_default5.csv t_smoke.csv && echo "default5_vs_smoke_scores2 IDENTICAL"
  cmp $OUT/default5/$BF $R/$BF && echo "default5_by_fold_vs_smoke_scores2 IDENTICAL"
  echo "merged_vs_unsharded rows $(wc -l < t_merged.csv) $(wc -l < t_unsharded.csv)"
  cmp t_merged.csv t_unsharded.csv && echo "merged_vs_unsharded IDENTICAL"
  cmp $OUT/merged/$BF $OUT/unsharded/$BF && echo "merged_by_fold_vs_unsharded IDENTICAL"
  echo "cqr rows merged $(grep -c ',cqr,' t_merged.csv) unsharded $(grep -c ',cqr,' t_unsharded.csv)"
  md5sum t_*.csv; rm -f t_*.csv
} > check_compare.txt 2>&1
grep -c IDENTICAL check_compare.txt > n_identical.txt
[ "$(cat n_identical.txt)" = "4" ] || echo 6 > rc_compare
RC=0
for f in rc_*; do [ -e "$f" ] || continue; v=$(cat "$f"); [ "$v" = "0" ] || RC=$v; done
ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "pre-commit check of the CQR gene-range option: snapshot $COMMIT with round10_final_runs_f3_map.py overlaid from $STAGED (md5 $DRIVER_MD5, see check_driver.txt); round3_a4_scores A4 anchor; scores default vs smoke_scores2; CCRCC:24 INT1 cal 0 unsharded vs 3 gene-range parts merged; LUNG 43-gene part timed" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'","driver_md5":"'$DRIVER_MD5'"}' --scripts code/scripts/round10_final_runs_f3_map_anchor.py code/scripts/round3_a4_scores.py code/scripts/round4_conf_c3.py code/scripts/round5_conf_w3.py code/scripts/round3_a0_harness.py --inputs $B/round3/task_defs/CCRCC.json $B/round3/A4_scores/a4_scores_by_task__uni_v2__mainCCRCC.csv $STAGED
cd "$OUT"
for g in PROVENANCE.txt _provenance.json *.json *.csv *.txt rc_*; do [ -e "$g" ] && cp "$g" "$HJ"/; done
for g in */*timing*.csv */*by_fold*.csv; do [ -e "$g" ] && cp "$g" "$HJ"/"$(echo $g | tr / _)"; done
true
for g in *.log; do [ -e "$g" ] && echo "=== $g" && tail -5 "$g"; done
exit 0
