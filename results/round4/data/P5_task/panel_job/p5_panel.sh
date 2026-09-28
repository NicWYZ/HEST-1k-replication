#!/bin/bash
#SBATCH -J r4data_p5panel
#SBATCH -A rc_htzhu_pi
#SBATCH -p general
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 00:15:00
set -euo pipefail
WD=$PWD; export PYTHONHASHSEED=0
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
mkdir -p $WD/out
echo "job=$SLURM_JOB_ID partition=$SLURM_JOB_PARTITION node=$(hostname) date=$(date -Is) script_md5=$(md5sum lung_panel.py | cut -c1-32)" > $WD/out/job_facts.txt
$PY lung_panel.py | tee -a $WD/out/job_facts.txt
mkdir -p "$WD/out"
cat > "$WD/out/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_3a4e23273fb6",
  "frame_id": "dab7c82a-7762-41ec-aaf1-9a41e6afaff2",
  "track": "Completion",
  "plan": "round4 stage P",
  "note": "P5 input: lung Xenium gene panels and intersection",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
