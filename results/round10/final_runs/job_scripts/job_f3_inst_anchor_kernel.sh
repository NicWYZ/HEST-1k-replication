#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=60
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
OUT=$BASE/F3/institution/anchor_kernel
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
  "frame_id": "b9c04725-eaea-4b47-8586-4ff29636ba08",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F3.2 anchor check 1: hcp kernel with donors as groups vs W3 row CCRCC uni_v2 INT1 K10 alpha 0.1 o 0",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
CMD="round10_final_runs_f3_institution.py anchor_kernel --w3-by-fold /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/conformal/W3_real/merged/w3_by_fold.csv --out $OUT"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 anchor_kernel $COMMIT $SNAP "$START" $ST --frame b9c04725-eaea-4b47-8586-4ff29636ba08 --command "$CMD" --config '{"stage":"F3","unit":"anchor_kernel","commit":"'$COMMIT'","task":"CCRCC:24","encoder":"uni_v2","K":10,"fold":"INT1","alpha":0.1}' --scripts code/scripts/round10_final_runs_f3_institution.py code/scripts/round4_conf_c3.py code/scripts/round4_conf_sim.py code/scripts/round4_conf_io.py code/scripts/round3_a0_harness.py code/scripts/round3_a4b_hcp.py --inputs /work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/conformal/W3_real/merged/w3_by_fold.csv /work/users/w/e/weiyang/hest_replication/results/round3/task_defs/CCRCC.json /work/users/w/e/weiyang/hest_replication/results/round3/D3_audit/donor_audit_r3.csv
cd "$OUT"; for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -60 stdout.log
exit $RC
