#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=30
set -u
UNIT=takeall_anchor_r9
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
  "note": "F3.3 (v) anchor: round9_probe_takeall.py unchanged on CCRCC, three candidate parquets",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
git -C "$CLONE" show $COMMIT:results/round9/probe/takeall_by_gene.csv.gz > "$OUT/ref_takeall_by_gene.csv.gz"
git -C "$CLONE" show $COMMIT:results/round9/probe/takeall_medians.csv > "$OUT/ref_takeall_medians.csv"
RC=0
mkdir -p $OUT/rerun_uni_v2 $OUT/rerun_hoptimus0 $OUT/rerun_resnet50
CMD1="round9_probe_takeall.py /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet CCRCC $OUT/rerun_uni_v2"
set +e
$PY -u $SNAP/code/scripts/$CMD1 > stdout_1.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMD2="round10_final_runs_f3_takeall.py anchor_check $OUT/rerun_uni_v2/takeall_by_gene__CCRCC.csv.gz $OUT/ref_takeall_by_gene.csv.gz $OUT/ref_takeall_medians.csv CCRCC $OUT/anchor_takeall_uni_v2.json"
set +e
$PY -u $SNAP/code/scripts/$CMD2 > stdout_2.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMD3="round9_probe_takeall.py /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__hoptimus0.parquet CCRCC $OUT/rerun_hoptimus0"
set +e
$PY -u $SNAP/code/scripts/$CMD3 > stdout_3.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMD4="round10_final_runs_f3_takeall.py anchor_check $OUT/rerun_hoptimus0/takeall_by_gene__CCRCC.csv.gz $OUT/ref_takeall_by_gene.csv.gz $OUT/ref_takeall_medians.csv CCRCC $OUT/anchor_takeall_hoptimus0.json"
set +e
$PY -u $SNAP/code/scripts/$CMD4 > stdout_4.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMD5="round9_probe_takeall.py /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__resnet50.parquet CCRCC $OUT/rerun_resnet50"
set +e
$PY -u $SNAP/code/scripts/$CMD5 > stdout_5.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMD6="round10_final_runs_f3_takeall.py anchor_check $OUT/rerun_resnet50/takeall_by_gene__CCRCC.csv.gz $OUT/ref_takeall_by_gene.csv.gz $OUT/ref_takeall_medians.csv CCRCC $OUT/anchor_takeall_resnet50.json"
set +e
$PY -u $SNAP/code/scripts/$CMD6 > stdout_6.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMDS="${CMD1} ; ${CMD2} ; ${CMD3} ; ${CMD4} ; ${CMD5} ; ${CMD6}"
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 $UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMDS" --config '{"stage":"F3","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round9_probe_takeall.py code/scripts/round10_final_runs_f3_takeall.py --inputs /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__hoptimus0.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__resnet50.parquet $OUT/ref_takeall_by_gene.csv.gz $OUT/ref_takeall_medians.csv
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout*.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -40 stdout*.log
exit $RC
