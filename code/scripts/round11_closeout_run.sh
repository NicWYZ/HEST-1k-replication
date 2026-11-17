#!/bin/bash
# Round 11, track closeout: the one Slurm wrapper every job of the track runs through.
# Submitted as: sbatch [slurm options] round11_closeout_run.sh <commit> <stage> <unit> "<note>" "<scripts>" "<inputs>" -- <script.py> <args...>
#   <unit> is the output directory relative to $BASE; it must not exist.
#   <scripts> space-separated paths relative to the snapshot (md5s recorded); <inputs> space-separated absolute paths.
#   The command after -- is run with the project's Python from the snapshot's code/scripts, inside the output directory.
# The job takes a read-only snapshot of <commit>'s code/ (git archive from the track's clone), stamps the output
# directory with the longleaf-provenance stamp on the node, and writes PROVENANCE.txt.
set -u
COMMIT=$1; STAGE=$2; UNIT=$3; NOTE=$4; SCRIPTS=$5; INPUTS=$6; shift 6
[ "$1" = "--" ] || { echo "expected --"; exit 2; }; shift
CLONE=/work/users/w/e/weiyang/hest_code/round11-closeout
BASE=/work/users/w/e/weiyang/hest_replication/results/round11/closeout
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
SNAP=$BASE/_snapshots/$COMMIT
OUT=$BASE/$UNIT
START=$(date -Iseconds)
exec 9>"$BASE/_snapshots/.lock"; flock 9
if [ ! -d "$SNAP" ]; then
  mkdir -p "$SNAP.tmp" && git -C "$CLONE" archive "$COMMIT" code | tar -x -C "$SNAP.tmp"
  (cd "$SNAP.tmp" && find code -type f \( -name '*.py' -o -name '*.sh' \) | sort | xargs md5sum > MD5SUMS)
  chmod -R a-w "$SNAP.tmp" && mv "$SNAP.tmp" "$SNAP"
fi
flock -u 9
if [ -e "$OUT" ]; then echo "OUT exists: $OUT, refusing"; exit 3; fi
mkdir -p "$OUT"
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_8450e231133d",
  "frame_id": "c9016697-c909-435e-82fc-ebfb9daaa857",
  "track": "closeout",
  "plan": "docs/round11/closeout/round11_closeout_plan.md",
  "note": "$STAGE $UNIT: $NOTE",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1} OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1} MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
SCRIPT=$1; shift
set +e
$PY -u "$SNAP/code/scripts/$SCRIPT" "$@" > stdout.log 2>&1; RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED
echo "rc=$RC start=$START end=$(date -Iseconds) slurm=${SLURM_JOB_ID:-} partition=${SLURM_JOB_PARTITION:-}" > runs.txt
$PY "$SNAP/code/scripts/round11_closeout_prov.py" write "$OUT" "$STAGE" "$UNIT" "$COMMIT" "$SNAP" "$START" "$ST" \
  --command "$SCRIPT $*" --config "{\"stage\":\"$STAGE\",\"unit\":\"$UNIT\",\"commit\":\"$COMMIT\"}" \
  --scripts code/scripts/$SCRIPT code/scripts/round11_closeout_prov.py code/scripts/round11_closeout_run.sh $SCRIPTS \
  --inputs $INPUTS
tail -5 stdout.log
[ "$ST" = COMPLETED ]
