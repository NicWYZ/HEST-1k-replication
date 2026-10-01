#SBATCH --account=rc_tengfei_pi
#SBATCH -p general
#SBATCH -n 4
#SBATCH --mem=8G
#SBATCH --time=00:30:00
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
print(h.__file__)
assert h.__file__.startswith("$CLONE"), h.__file__
PYEOF
HARNESS_MD5=$(md5sum $CLONE/code/scripts/round3_a0_harness.py | cut -d" " -f1)
echo "harness md5 $HARNESS_MD5"
echo "== install (pip --target, no project env)"
$PY -m pip install --target $LIBS --no-deps ppi-python 2>&1 | tail -3
$PY -m pip install --target $LIBS gdown 2>&1 | tail -3
$PY -m pip --version
echo "== retire stale attempt-1 files (attempt 1 failed on a gdown import error in my setup, not a network refusal)"
[ -f $OUTDIR/REFUSAL.txt ] && mv $OUTDIR/REFUSAL.txt $OUTDIR/attempt1_FAILED_gdown_import_NOT_a_refusal.txt
[ -f $OUTDIR/REFUSAL_candidate_stdout.txt ] && mv $OUTDIR/REFUSAL_candidate_stdout.txt $OUTDIR/attempt1_stdout.txt
echo "== fetch"
cd $WD
FETCH_CMD="$PY acs_fetch.py $OUTDIR $LIBS"
set +e
$FETCH_CMD 2>&1 | tee fetch_stdout.txt
RC=${PIPESTATUS[0]}
set -e
echo "fetch rc=$RC"
if [ ! -s $OUTDIR/census_income.npz ]; then
  cp fetch_stdout.txt $OUTDIR/REFUSAL_candidate_stdout.txt
  cat > $OUTDIR/REFUSAL.txt <<EOF
Download did not produce census_income.npz.
command: $FETCH_CMD  (loader: ppi_py.datasets.load_dataset(folder, "census_income"), which shells out to gdown with Google Drive id 15dZeWw-RTw17-MieG4y1ILTZlreJOmBS)
exit code of script: $RC
--- output ---
$(tail -40 fetch_stdout.txt)
EOF
fi
cp acs_fetch.py $OUTDIR/
PVER=$($PY -c "import glob,os;print([os.path.basename(d) for d in glob.glob('$LIBS/ppi_python-*.dist-info')])")
{
echo "stage: r4ppi_Q0 unit acs_data (fetch)"
echo "intended job prefix: r4ppi_ (identified by slurm id)"
echo "slurm_job_id: $SLURM_JOB_ID"
echo "partition: $SLURM_JOB_PARTITION"
echo "node: $(hostname)"
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit (clone HEAD): $(git -C $CLONE rev-parse HEAD)"
echo "clone: $CLONE ; harness round3_a0_harness.py md5: $HARNESS_MD5 (imported from clone, path asserted)"
echo "command: $FETCH_CMD"
echo "pythonhashseed: $PYTHONHASHSEED"
echo "source: ppi_py.datasets.load_dataset dataset 'census_income'; Google Drive file id 15dZeWw-RTw17-MieG4y1ILTZlreJOmBS (https://drive.google.com/uc?id=15dZeWw-RTw17-MieG4y1ILTZlreJOmBS), fetched by gdown"
echo "ppi_py dist-info: $PVER (installed with pip --target $LIBS)"
echo "config hash: none (no config; the fetch has no parameters beyond the dataset name)"
echo "script md5: $(md5sum acs_fetch.py)"
echo "files:"
md5sum $OUTDIR/*.npz 2>/dev/null; sha256sum $OUTDIR/*.npz 2>/dev/null
} > $OUTDIR/PROVENANCE.txt
cat $OUTDIR/PROVENANCE.txt
ls -lh $OUTDIR
