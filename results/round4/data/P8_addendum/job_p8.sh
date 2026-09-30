#SBATCH -A rc_htzhu_pi
#SBATCH -p general
#SBATCH -n 4
#SBATCH --mem=16G
#SBATCH -t 00:30:00
set -eo pipefail
WD=$PWD
export PYTHONHASHSEED=0
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
mkdir -p "$WD"
cat > "$WD/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_3a4e23273fb6",
  "frame_id": "dab7c82a-7762-41ec-aaf1-9a41e6afaff2",
  "track": "P8 addendum",
  "plan": "round4 stage P8 (docs/round4_data_plan.md section 9)",
  "note": "subset relation after the NCBI865 drop and the lung edge-patch diagnostic; report only",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
{ echo "stage            : round4 P8 (subset after drop; lung edge-patch diagnostic)"
  echo "intended_job_name: r4data_p8_longleaf (the submission route replaces --job-name)"
  echo "slurm_job_id     : $SLURM_JOB_ID"; echo "slurm_partition  : $SLURM_JOB_PARTITION"; echo "node             : $(hostname)"
  echo "date             : $(date -Is)"; echo "commit           : $(git -C /work/users/w/e/weiyang/hest_replication rev-parse HEAD)"
  echo "command          : $PY round4_data_p8_longleaf.py"; echo "PYTHONHASHSEED   : $PYTHONHASHSEED"
  echo "script md5       : $(md5sum round4_data_p8_longleaf.py | cut -d' ' -f1)"
  echo "config md5       : $(md5sum p8_config.json | cut -d' ' -f1)  (p8_config.json, alongside)"
  echo "writes           : this job directory only; reads hest_ext/lung_xenium/{patches,st}"; } > PROVENANCE.txt
$PY round4_data_p8_longleaf.py | tee p8_longleaf_stdout.txt
