#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=90
set -u
UNIT=bal_smoke
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
  "note": "F3.3 (iv) smoke: CCRCC and LUNG_XENIUM uni_v2 log1p theta3 n_L 8, every design, timed",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
git -C "$CLONE" show $COMMIT:results/round10/final_runs/F3/configs/balance/f3_bal__smoke.json > "$OUT/f3_bal__smoke.json"
CFG=f3_bal__smoke.json
INPUTS=$($PY -c "import json,sys;c=json.load(open(sys.argv[1]));ps=c.get('populations',[]);print(' '.join(sorted(set([p.get(k) for p in ps for k in ('parquet','path','morph_path','cluster_values','spots_path') if p.get(k)]+c.get('cluster_values',[])+c.get('regimeA_cells',[])))))" "$OUT/$CFG")
RC=0
CMD1="round10_final_runs_f3_balance.py $OUT/$CFG $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD1 > stdout_1.log 2>&1
R=$?; [ $RC -eq 0 ] && RC=$R
set -e
CMDS="${CMD1}"
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 $UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMDS" --config '{"stage":"F3","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_balance.py code/scripts/round5_ppi_balance.py code/scripts/round5_ppi_e4_selection.py code/scripts/round7_ppi_s4b_cube3.py code/scripts/round7_ppi_s3_cube.py code/scripts/round7_ppi_weighting.py code/scripts/round4_ppi_estimator.py code/scripts/round5_ppi_estimator.py code/scripts/round5_ppi_common.py code/scripts/round5_ppi_e2_regimeB.py code/scripts/round4_ppi_q2_masking.py code/scripts/round3_b1_ppi.py code/scripts/round4_ppi_q3_regimes.py --inputs $OUT/$CFG $INPUTS
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout*.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -n 40 stdout*.log
exit $RC
