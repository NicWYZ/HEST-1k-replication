#SBATCH --account=rc_htzhu_pi
#SBATCH -p general
#SBATCH -n 4
#SBATCH --mem=4G
#SBATCH --time=00:30:00
export PYTHONHASHSEED=0
REPO=/work/users/w/e/weiyang/hest_replication
PY=$REPO/env/miniforge3/envs/hest/bin/python
OUTDIR=$REPO/results/round4/ppi/Q0_setup/lung_wrapper
WD=$(pwd)
CLONE=/work/users/w/e/weiyang/hest_code/round4-ppi
export CLONE
export R4PPI_CODE_DIR=$CLONE/code/scripts
export PYTHONPATH=$CLONE/code/scripts:$PYTHONPATH
cd $WD
mkdir -p "$OUTDIR"
cat > "$OUTDIR/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_3a4e23273fb6",
  "frame_id": "489504c4-ba56-4908-816f-a5c52417f390",
  "track": "r4ppi_Q0",
  "plan": "round4_ppi",
  "note": "Q0 lung wrapper check on NCBI865 and 20 lung samples",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
CMD="$PY q0_lung_wrapper_check.py $OUTDIR"
$CMD 2>&1 | tee $OUTDIR/job_stdout.txt
cp q0_lung_wrapper_config.json $OUTDIR/
cp round4_ppi_data.py q0_lung_wrapper_check.py $OUTDIR/
CFGH=$(md5sum q0_lung_wrapper_config.json | cut -d' ' -f1)
{
echo "stage: r4ppi_Q0 lung_wrapper"
echo "intended_job_prefix: r4ppi_ (job identified by Slurm id)"
echo "slurm_job_id: $SLURM_JOB_ID"
echo "partition: $SLURM_JOB_PARTITION"
echo "node: $(hostname)"
echo "date_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit: $(git -C $CLONE rev-parse HEAD)"
echo "command: $CMD  (R4PPI_CODE_DIR=$R4PPI_CODE_DIR)"
echo "config_file: q0_lung_wrapper_config.json  config_md5: $CFGH"
echo "PYTHONHASHSEED: $PYTHONHASHSEED"
echo "clone_harness_md5: $(md5sum $CLONE/code/scripts/round3_a0_harness.py | cut -d' ' -f1)"
echo "script_md5:"
md5sum round4_ppi_data.py q0_lung_wrapper_check.py $CLONE/code/scripts/round3_d4_sets.py $CLONE/code/scripts/round3_a0_harness.py $CLONE/code/scripts/round3_a3_weighted.py $CLONE/code/scripts/round2_r2_gene_check.py
} > $OUTDIR/PROVENANCE.txt
mkdir -p out && cp $OUTDIR/* out/
cat $OUTDIR/PROVENANCE.txt
ls -lh out || true
