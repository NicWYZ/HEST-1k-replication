#!/bin/bash
# usage: sbatch ... common.sh <name> <script.py>
# runs from $BASE/<name>/, writes _provenance.json and PROVENANCE.txt
set -u
BASE=/work/users/w/e/weiyang/hest_replication/results/round11/closeout/fcheck
NAME=$1; SCRIPT=$2
OUT=$BASE/$NAME
mkdir -p $OUT; cd $OUT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
export PYTHONHASHSEED=0
cat > _provenance.json <<JSON
{"project_id": "proj_8450e231133d", "frame_id": "c9016697-c909-435e-82fc-ebfb9daaa857/fcheck", "track": "closeout", "plan": "docs/round11/closeout/round11_closeout_plan.md", "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "note": "fresh check before G-final ($NAME)", "host": "$(hostname)", "writer": "claude-science"}
JSON
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
$PY -I $BASE/scripts/$SCRIPT > stdout.log 2> stderr.log
RC=$?
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
echo "slurm_job_id: ${SLURM_JOB_ID:-none}"
echo "partition: ${SLURM_JOB_PARTITION:-none}"
echo "node: $(hostname)"
echo "start: $START"; echo "end: $END"; echo "exit: $RC"
echo "command: $PY -I $BASE/scripts/$SCRIPT"
echo "PYTHONHASHSEED=$PYTHONHASHSEED"
echo "script md5: $(md5sum $BASE/scripts/$SCRIPT)"
echo "wrapper md5: $(md5sum $BASE/scripts/common.sh)"
echo "inputs md5:"; [ -f inputs.txt ] && while read f; do md5sum "$f"; done < inputs.txt
} > PROVENANCE.txt
