#!/bin/bash
# b1 job wrapper. usage (from the output dir): sbatch ... b1_job.sh <script.py> [inputs...] -- [extra args]
# Runs <script.py> <out_dir> [inputs...] [extra args], with stamp and PROVENANCE.txt written on the node.
set -euo pipefail
OUT="$(pwd)"
SCR=/work/users/w/e/weiyang/hest_replication/results/round11/closeout/b1/scripts
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
export PYTHONHASHSEED=0
SCRIPT="$1"; shift
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_8450e231133d",
  "frame_id": "c9016697-c909-435e-82fc-ebfb9daaa857/b1",
  "track": "closeout",
  "plan": "docs/round11/closeout/round11_closeout_plan.md",
  "note": "B1 independent recomputation of the headline numbers: $SCRIPT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
{
  echo "platform: Longleaf"
  echo "slurm_job_id: ${SLURM_JOB_ID:-none}"
  echo "slurm_job_partition: ${SLURM_JOB_PARTITION:-none}"
  echo "slurm_job_account: ${SLURM_JOB_ACCOUNT:-none}"
  echo "node: $(hostname)"
  echo "frame_id: c9016697-c909-435e-82fc-ebfb9daaa857/b1"
  echo "track: closeout (round 11), sub-agent b1 (brief Part B item 1)"
  echo "PYTHONHASHSEED: $PYTHONHASHSEED"
  echo "python: $PY"
  echo "start: $(date -Iseconds)"
  echo "command: $PY $SCR/$SCRIPT $OUT $*"
  echo "snapshot_commit: none (b1 scripts are sub-agent verification scripts, not repository code; md5s below)"
  echo "scripts (md5):"
  md5sum "$SCR/$SCRIPT" "$SCR/b1_provenance_kernel.py" "$SCR/b1_job.sh" | sed 's/^/  /'
  echo "inputs (md5):"
  for a in "$@"; do
    if [ -f "$a" ]; then md5sum "$a" | sed 's/^/  /'; fi
  done
} > "$OUT/PROVENANCE.txt"
set +e
"$PY" "$SCR/$SCRIPT" "$OUT" "$@" > "$OUT/stdout.log" 2> "$OUT/stderr.log"
RC=$?
set -e
{
  echo "input_files_read_by_script (md5): see inputs_md5.txt if written"
  echo "end: $(date -Iseconds)"
  echo "exit_code: $RC"
  echo "status: $([ $RC -eq 0 ] && echo COMPLETED || echo FAILED)"
} >> "$OUT/PROVENANCE.txt"
exit $RC
