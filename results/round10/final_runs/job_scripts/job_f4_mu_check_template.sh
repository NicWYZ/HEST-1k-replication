#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=__MEM__
#SBATCH --time=__TIME__
set -u
# F4 mu check (plan 5e.1): mode __MODE__. Template; __UNIT__, __CODE_COMMIT__, __MODE__, __ARG__, __MEM__ and __TIME__ are substituted at submission.
UNIT=__UNIT__
MODE=__MODE__
ARG=__ARG__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=bdb361de-6630-44e8-b0f8-8bd63dae9ad3
HJ=$PWD
OUT=$BASE/F4/mu_check/$UNIT
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
  "note": "F4 mu check (plan 5e.1), mode $MODE, unit $UNIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2
$PY -u $SNAP/code/scripts/round10_final_runs_f4_mu_check.py $MODE $ARG "$OUT" > stdout.log 2>&1; RC=$?
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F4 "mu_check/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round10_final_runs_f4_mu_check.py $MODE $ARG $OUT" --config '{"stage":"F4","unit":"'$UNIT'","mode":"'$MODE'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f4_mu_check.py code/scripts/round10_final_runs_f2_regimeB.py code/scripts/round10_final_runs_f3_regcomp.py code/scripts/round10_final_runs_f3_box.py code/scripts/round10_final_runs_f3_regimeB.py --inputs $( [ -d "$ARG" ] && ls "$ARG"/f3_box__*.json || echo "$ARG" )
for g in PROVENANCE.txt _provenance.json stdout.log *.json *.csv; do [ -e "$g" ] && cp "$g" "$HJ"/; done; true
tail -30 stdout.log
exit 0
