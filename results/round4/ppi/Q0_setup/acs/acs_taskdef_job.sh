#SBATCH --account=rc_tengfei_pi
#SBATCH -p general
#SBATCH -n 4
#SBATCH --mem=4G
#SBATCH --time=00:15:00
export PYTHONHASHSEED=0
REPO=/work/users/w/e/weiyang/hest_replication
CLONE=/work/users/w/e/weiyang/hest_code/round4-ppi
export PYTHONPATH=$CLONE/code/scripts:/work/users/w/e/weiyang/round4_ppi_pylibs:$PYTHONPATH
PY=$REPO/env/miniforge3/envs/hest/bin/python
LIBS=/work/users/w/e/weiyang/round4_ppi_pylibs
OUTDIR=$REPO/results/round4/ppi/Q0_setup/acs
mkdir -p $LIBS
WD=$(pwd)
mkdir -p "$OUTDIR"
cat > "$OUTDIR/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_3a4e23273fb6",
  "frame_id": "a1c8b6e7-3129-4be0-9247-9a5438941cac",
  "track": "r4ppi_Q0_acs",
  "plan": "round4_ppi_plan",
  "note": "ACS census_income fetch via ppi_py, Q0 step 3",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF

echo "== clone module path check"
$PY - <<PYEOF
import round3_a0_harness as h
assert h.__file__.startswith("$CLONE"), h.__file__
print(h.__file__)
PYEOF
HARNESS_MD5=$(md5sum $CLONE/code/scripts/round3_a0_harness.py | cut -d" " -f1)
cd $WD
OUTDEF=$REPO/results/round4/ppi/Q0_setup/acs_task_def.json
[ ! -e $OUTDEF ] || { echo "acs_task_def.json already exists, refusing to overwrite"; exit 3; }
CMD="$PY acs_taskdef.py $OUTDIR $OUTDEF $OUTDIR/acs_inventory.json"
$CMD | tee taskdef_stdout.txt
{
echo "stage: r4ppi_Q0 unit acs_data (inventory and task definition)"
echo "intended job prefix: r4ppi_ (identified by slurm id)"
echo "slurm_job_id: $SLURM_JOB_ID"; echo "partition: $SLURM_JOB_PARTITION"; echo "node: $(hostname)"
echo "account: $(sacct -j $SLURM_JOB_ID -X -n -P -o Account 2>/dev/null)"
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit (clone HEAD): $(git -C $CLONE rev-parse HEAD)"
echo "clone: $CLONE ; harness round3_a0_harness.py md5: $HARNESS_MD5 (imported from clone, path asserted)"
echo "command: $CMD"; echo "pythonhashseed: $PYTHONHASHSEED"
echo "config hash: none (no config file; parameters are the three path arguments)"
echo "script md5: $(md5sum acs_taskdef.py)"
echo "outputs md5:"; md5sum $OUTDEF $OUTDIR/acs_inventory.json
} > $OUTDIR/PROVENANCE_taskdef.txt
cat $OUTDIR/PROVENANCE_taskdef.txt
