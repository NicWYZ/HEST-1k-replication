#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=62
set -u
UNIT=regcomp__pk_bowel__Visium__resnet50__lognorm__p04
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=2c7941c3-ecf2-4306-a6d1-ae6170b4cbe8
HJ=$PWD
OUT=$BASE/F3/regimeB/$UNIT
START=$(date -Iseconds)
case "$COMMIT" in __*) echo "COMMIT placeholder not substituted"; exit 4;; esac
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
  "note": "F3 5d.3 (i), regime A against regime B cost-matched, packed unit pk_bowel__Visium__resnet50__lognorm__p04",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
git -C "$CLONE" show $COMMIT:results/round10/final_runs/F3/configs/regcomp/f3_regcomp__pk_bowel__Visium__resnet50__lognorm__p04.json > "$OUT/f3_regcomp__pk_bowel__Visium__resnet50__lognorm__p04.json"
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
set +e
RC=0
CMDS=""
CMD0="round10_final_runs_f3_regcomp.py run $OUT/f3_regcomp__pk_bowel__Visium__resnet50__lognorm__p04.json $OUT"
CMDS="$CMDS${CMDS:+ ; }$CMD0"
$PY -u $SNAP/code/scripts/$CMD0 > stdout.log 2>&1
R_=$?; [ $R_ -ne 0 ] && RC=$R_
echo "step 0 rc $R_" >> stdout.log
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
INPUTS=$($PY -c "import json,os,sys
out=sys.argv[1]; s=set()
def w(x):
    if isinstance(x,dict): [w(v) for v in x.values()]
    elif isinstance(x,list): [w(v) for v in x]
    elif isinstance(x,str) and x.startswith('/work/') and not x.startswith(out) and os.path.isfile(x): s.add(x)
for p in sys.argv[2:]: w(json.load(open(p)))
print(' '.join(sorted(s)))" "$OUT" "$OUT/f3_regcomp__pk_bowel__Visium__resnet50__lognorm__p04.json")
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 $UNIT $COMMIT $SNAP "$START" $ST --frame $FRAME --command "$CMDS" --config '{"stage":"F3","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_estimators.py code/scripts/round10_final_runs_f2_regimeB.py code/scripts/round10_final_runs_f3_regcomp.py code/scripts/round3_b1_ppi.py code/scripts/round4_ppi_estimator.py code/scripts/round4_ppi_q2_masking.py code/scripts/round4_ppi_q3_regimes.py code/scripts/round5_ppi_e2_regimeB.py code/scripts/round5_ppi_e3_twolevel.py code/scripts/round5_ppi_estimator.py code/scripts/round5_ppi_twolevel.py --inputs "$OUT/f3_regcomp__pk_bowel__Visium__resnet50__lognorm__p04.json" $INPUTS
cd "$OUT"; for g in $(find . -maxdepth 2 -type f \( -name "*.json" -o -name "*.csv" -o -name "*.txt" -o -name "*.log" \) -size -20M); do [ -e "$g" ] && cp "$g" "$HJ/$(echo ${g#./} | tr / _)"; done; true
tail -40 stdout.log; for f in stdout*.log; do [ -e "$f" ] && tail -15 "$f"; done; true
exit $RC
