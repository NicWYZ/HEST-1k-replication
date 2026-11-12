#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=30
set -u
UNIT=bal_anchor_e4b
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
  "note": "F3.3 (iv) anchor 1: round5_ppi_e4b_rejective.py unchanged, CCRCC uni_v2 theta3 n_L 8 (Slurm 4382135's command)",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
git -C "$CLONE" show $COMMIT:results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv > "$OUT/ref_e4b_rej_width_ratios.csv"
RC=0
CMD1="round5_ppi_e4b_rejective.py --parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet --perm-parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__resnet50.parquet --ref-parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__resnet50.parquet --ref-arm resnet50 --vtag CCRCC --arm uni_v2 --estimands theta3 --nl-grid 8 --out-dir $OUT/rerun"
set +e
$PY -u $SNAP/code/scripts/$CMD1 > stdout_1.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMD2="round10_final_runs_f3_balance_anchor.py e4b $OUT/rerun CCRCC__uni_v2 $OUT/ref_e4b_rej_width_ratios.csv /work/users/w/e/weiyang/hest_replication/results/round5/ppi/E4b_rejective/CCRCC/uni_v2/theta3_nL8/e4b_rejective_genes__CCRCC__uni_v2.csv.gz $OUT/anchor_e4b.json"
set +e
$PY -u $SNAP/code/scripts/$CMD2 > stdout_2.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMDS="${CMD1} ; ${CMD2}"
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 $UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMDS" --config '{"stage":"F3","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round3_b1_ppi.py code/scripts/round4_ppi_estimator.py code/scripts/round4_ppi_q2_masking.py code/scripts/round4_ppi_q3_regimes.py code/scripts/round5_ppi_balance.py code/scripts/round5_ppi_common.py code/scripts/round5_ppi_e2_regimeB.py code/scripts/round5_ppi_e4_selection.py code/scripts/round5_ppi_estimator.py code/scripts/round5_ppi_e4b_rejective.py code/scripts/round10_final_runs_f3_balance_anchor.py --inputs /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__resnet50.parquet /work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q5_joint/q5_mean_embeddings__CCRCC__uni_v2.parquet $OUT/ref_e4b_rej_width_ratios.csv /work/users/w/e/weiyang/hest_replication/results/round5/ppi/E4b_rejective/CCRCC/uni_v2/theta3_nL8/e4b_rejective_genes__CCRCC__uni_v2.csv.gz
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout*.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -n 40 stdout*.log
exit $RC
