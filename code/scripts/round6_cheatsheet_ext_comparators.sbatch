#!/bin/bash
#SBATCH --job-name=r6ext_comparators
#SBATCH --account=rc_htzhu_pi
#SBATCH -p general
#SBATCH -n 8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=/work/users/w/e/weiyang/hest_replication/results/round6/cheatsheet_ext/C4_comparators/r6ext_comparators_%j.log
# Round 6 extension, cheatsheet track, C4.4: the anchor and the comparators.
# Submit from the code clone on Longleaf with
#   sbatch --export=ALL,COMMIT=<full hash>,PACKAGE=<package directory> code/scripts/round6_cheatsheet_ext_comparators.sbatch
# The job copies COMMIT's scripts and round 1's two split-0 folders with git archive into its own output
# directory, runs from that copy, and reads the project tree read-only.
set -euo pipefail
: "${COMMIT:?set COMMIT to the full commit hash}"
: "${PACKAGE:?set PACKAGE to the package directory of the C4.3 job}"
CLONE=${CLONE:-$SLURM_SUBMIT_DIR}
PROJ=/work/users/w/e/weiyang/hest_replication
PY=$PROJ/env/miniforge3/envs/hest/bin/python
OUT=$PROJ/results/round6/cheatsheet_ext/C4_comparators/job_${SLURM_JOB_ID}
FRAME_ID=r6ext_comparators_${SLURM_JOB_ID}
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=8

mkdir -p "$OUT/code"
cd "$OUT"
git -C "$CLONE" cat-file -e "${COMMIT}^{commit}"
git -C "$CLONE" archive "$COMMIT" code/scripts/round6_cheatsheet_ext_comparators.py code/scripts/round6_cheatsheet_ext_comparators.sbatch code/scripts/round6_cheatsheet_ext_score.py code/scripts/round6_cheatsheet_comparators.py code/scripts/round6_cheatsheet_score.py results/faithful/pca_ridge/uni_v2/CCRCC/split0 results/faithful/pca_ridge/virchow2/CCRCC/split0 | tar -x -C "$OUT/code"
chmod -R a-w "$OUT/code"
SCRIPT=$OUT/code/code/scripts/round6_cheatsheet_ext_comparators.py

# provenance stamp, the fields of the longleaf-provenance skill's stamp
cat > "$OUT/_provenance.json" <<EOF
{"writer": "claude-code-local", "project_id": "proj_3a4e23273fb6", "frame_id": "$FRAME_ID",
 "track": "round6-cheatsheet-ext", "plan": "round06_cheatsheet_ext_plan", "note": "C4.4 anchor and comparators",
 "host": "$(hostname)", "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"}
EOF

CMD="$PY $SCRIPT --proj $PROJ --package $PACKAGE --out tables"
START=$(date +%s)
set +e
$CMD > comparators_stdout.txt 2> comparators_stderr.txt
RC=$?
set -e
END=$(date +%s)

cat > "$OUT/PROVENANCE.txt" <<EOF
stage: C4.4 anchor and comparators
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
package: $PACKAGE
package_manifest_md5: $(md5sum "$PACKAGE/MANIFEST.tsv" | cut -d' ' -f1)
script_md5:
$(cd "$OUT/code" && find . -type f | sort | xargs md5sum | sed 's/^/  /')
exit_code: $RC
wall_seconds: $((END - START))
EOF
cp PROVENANCE.txt _provenance.json tables/ 2>/dev/null || true
echo "exit $RC, output in $OUT"
exit $RC
