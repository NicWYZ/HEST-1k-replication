#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=15
set -u
UNIT=alloc_anchor_r5
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
FRAME=7bae80ef-cb3f-4725-8012-f680940d6c59
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F3/designs/$UNIT
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
  "note": "F3.3 (iii) anchor: round5_ppi_e5_allocation.py unchanged on round 5's committed E3 CSVs",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$OUT/results/round5/ppi/E3_twolevel" "$OUT/results/round5/ppi/E5_joint"
git -C "$CLONE" show $COMMIT:results/round5/ppi/E3_twolevel/e3_components.csv > "$OUT/results/round5/ppi/E3_twolevel/e3_components.csv"
git -C "$CLONE" show $COMMIT:results/round5/ppi/E3_twolevel/e3_masking_grid.csv > "$OUT/results/round5/ppi/E3_twolevel/e3_masking_grid.csv"
git -C "$CLONE" show $COMMIT:results/round5/ppi/E3_twolevel/e3_components_fitted.csv > "$OUT/results/round5/ppi/E3_twolevel/e3_components_fitted.csv"
git -C "$CLONE" show $COMMIT:results/round5/ppi/E5_joint/e5_allocation.csv > "$OUT/ref_e5_allocation.csv"
RC=0
CMD1="round5_ppi_e5_allocation.py"
set +e
$PY -u $SNAP/code/scripts/$CMD1 > stdout_1.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMD2="round10_final_runs_f3_allocation.py anchor_check $OUT/results/round5/ppi/E5_joint/e5_allocation.csv $OUT/ref_e5_allocation.csv $OUT/anchor_alloc.json"
set +e
$PY -u $SNAP/code/scripts/$CMD2 > stdout_2.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMDS="${CMD1} ; ${CMD2}"
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 $UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMDS" --config '{"stage":"F3","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round5_ppi_e5_allocation.py code/scripts/round10_final_runs_f3_allocation.py --inputs $OUT/results/round5/ppi/E3_twolevel/e3_components.csv $OUT/results/round5/ppi/E3_twolevel/e3_masking_grid.csv $OUT/results/round5/ppi/E3_twolevel/e3_components_fitted.csv $OUT/ref_e5_allocation.csv
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout*.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -n 40 stdout*.log
exit $RC
