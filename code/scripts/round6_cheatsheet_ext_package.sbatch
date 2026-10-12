#!/bin/bash
#SBATCH --job-name=r6ext_package
#SBATCH --account=rc_htzhu_pi
#SBATCH -p general
#SBATCH -n 4
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=/work/users/w/e/weiyang/hest_replication/results/round6/cheatsheet_ext/C4_package/r6ext_package_%j.log
# Round 6 extension, cheatsheet track, C4.3: the data package.
# Submit from the code clone on Longleaf with
#   sbatch --export=ALL,COMMIT=<full hash> code/scripts/round6_cheatsheet_ext_package.sbatch
# The job copies COMMIT's two scripts with git archive into its own output
# directory, runs from that copy, and reads the project tree read-only.
set -euo pipefail
: "${COMMIT:?set COMMIT to the full commit hash}"
CLONE=${CLONE:-$SLURM_SUBMIT_DIR}
PROJ=/work/users/w/e/weiyang/hest_replication
PY=$PROJ/env/miniforge3/envs/hest/bin/python
OUT=$PROJ/results/round6/cheatsheet_ext/C4_package/job_${SLURM_JOB_ID}
FRAME_ID=r6ext_package_${SLURM_JOB_ID}
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=4

mkdir -p "$OUT/code"
cd "$OUT"
git -C "$CLONE" cat-file -e "${COMMIT}^{commit}"
git -C "$CLONE" archive "$COMMIT" code/scripts/round6_cheatsheet_ext_package.py code/scripts/round6_cheatsheet_ext_package.sbatch | tar -x -C "$OUT/code"
chmod -R a-w "$OUT/code"
SCRIPT=$OUT/code/code/scripts/round6_cheatsheet_ext_package.py

# provenance stamp, the fields of the longleaf-provenance skill's stamp
cat > "$OUT/_provenance.json" <<EOF
{"writer": "claude-code-local", "project_id": "proj_3a4e23273fb6", "frame_id": "$FRAME_ID",
 "track": "round6-cheatsheet-ext", "plan": "round06_cheatsheet_ext_plan", "note": "C4.3 data package",
 "host": "$(hostname)", "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"}
EOF

CMD="$PY $SCRIPT --proj $PROJ --out package"
START=$(date +%s)
set +e
$CMD > package_stdout.txt 2> package_stderr.txt
RC=$?
set -e
END=$(date +%s)

cat > "$OUT/PROVENANCE.txt" <<EOF
stage: C4.3 data package
frame_id: $FRAME_ID
slurm_job_id: $SLURM_JOB_ID
partition: ${SLURM_JOB_PARTITION:-}
account: ${SLURM_JOB_ACCOUNT:-}
node: $(hostname)
date_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)
code_commit: $COMMIT
code_clone: $CLONE
command: $CMD
PYTHONHASHSEED: $PYTHONHASHSEED
python: $($PY -c 'import sys; print(sys.version.split()[0])') at $PY
versions: $($PY -c 'import numpy, pandas, pyarrow, h5py, anndata, PIL, sklearn; print("numpy", numpy.__version__, "pandas", pandas.__version__, "pyarrow", pyarrow.__version__, "h5py", h5py.__version__, "anndata", anndata.__version__, "Pillow", PIL.__version__, "scikit-learn", sklearn.__version__)')
script_md5:
  $(md5sum "$SCRIPT")
  $(md5sum "$OUT/code/code/scripts/round6_cheatsheet_ext_package.sbatch")
exit_code: $RC
wall_seconds: $((END - START))
EOF
if [ $RC -eq 0 ]; then
  cp PROVENANCE.txt _provenance.json package/
  # the manifest was written before these two were copied in, so add them
  for f in PROVENANCE.txt _provenance.json; do
    printf "%s\t%s\t%s\n" "$f" "$(stat -c %s package/$f)" "$(md5sum package/$f | cut -d' ' -f1)" >> package/MANIFEST.tsv
  done
fi
echo "exit $RC, output in $OUT"
exit $RC
