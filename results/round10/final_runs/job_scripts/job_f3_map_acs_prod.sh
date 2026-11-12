#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=30
set -u
UNIT=acs_prod
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
  "note": "E8 set side, ACS by state: round 4 code with within_full, 20 draws, o grid joined with the map grid",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
S=$SNAP/code/scripts
export PYTHONHASHSEED=0 PYTHONPATH=$S OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
M="$PY -u $S/round10_final_runs_f3_map.py"
set +e
( $M acs --pred $B/round4/ppi/Q0_setup/acs_pums2018/acs_pums2018_predictions.parquet --out $OUT/acs --draws 0-19 --workers 4 > acs.log 2>&1; echo $? > rc_acs
  $PY -u $S/round10_final_runs_f3_map_anchor.py acs $OUT/acs/acs_o_sweep.csv $CLONE/results/round4/conformal/C3_real/frag_ACS_o/c3_o_sweep__ACS.csv $OUT > anchor_acs.log 2>&1; echo $? > rc_anchor_acs )
[ -e $OUT/acs/acs_o_sweep.csv ] && cp $OUT/acs/acs_o_sweep.csv $OUT/acs_o_sweep.csv
RC=0
for f in rc_*; do [ -e "$f" ] || continue; v=$(cat "$f"); [ "$v" = "0" ] || RC=$v; done
ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $S/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round10_final_runs_f3_map.py acs --draws 0-19 --workers 4" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_map.py code/scripts/round10_final_runs_f3_map_anchor.py code/scripts/round10_final_runs_f3_map_aggregate.py code/scripts/round5_conf_w3.py code/scripts/round4_conf_sim.py code/scripts/round4_conf_c3.py --inputs $B/round4/ppi/Q0_setup/acs_pums2018/acs_pums2018_predictions.parquet $CLONE/results/round4/conformal/C3_real/frag_ACS_o/code/round4_conf_c3_acs_o.py $CLONE/results/round4/conformal/C3_real/frag_ACS_o/c3_o_sweep__ACS.csv
cd "$OUT"
for g in PROVENANCE.txt _provenance.json *.json *.csv rc_*; do [ -e "$g" ] && cp "$g" "$HJ"/; done
for g in */*.json */*timing*.csv */*by_fold*.csv */*summary*.csv */*compare*.csv */map_p103.csv; do [ -e "$g" ] && cp "$g" "$HJ"/"$(echo $g | tr / _)"; done
true
for g in *.log; do [ -e "$g" ] && echo "=== $g" && tail -8 "$g"; done
exit 0
