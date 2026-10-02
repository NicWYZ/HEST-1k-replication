#!/bin/bash
# usage: run_one.sh ARM NL
ARM=$1; NL=$2
export PYTHONHASHSEED=0 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
W=$(pwd)
S=/Users/nicolaszhang/HEST-1k-replication-PPI/code/scripts
ENC=$ARM; [ "$ARM" = permuted ] && ENC=resnet50
PQ=$W/hpc/scp-713a0994673a7eda/b1_predictions__LUNG_XENIUM__$ENC.parquet
OUT=$W/q2local/LUNG_XENIUM__$ARM/nL$NL
[ -e "$OUT/q2_summary__LUNG_XENIUM__$ARM.json" ] && { echo EXISTS $OUT; exit 3; }
mkdir -p $OUT
cat > $OUT/_provenance.json <<P
{"writer":"claude-science","project_id":"proj_3a4e23273fb6","frame_id":"040a77a6-04af-44f8-9fc3-a5a62d075ff8","track":"r4ppi_Q2_lung","plan":"round4_ppi","note":"Q2 masking LUNG_XENIUM arm $ARM nL $NL (local run)","host":"$(hostname)","created_at":"$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"}
P
CMD="python $S/round4_ppi_q2_masking.py --parquet $PQ --vtag LUNG_XENIUM --arm $ARM --nl-grid $NL --draws 200 --out-dir $OUT"
T0=$(date +%s)
$CMD > $OUT/job_stdout.txt 2>&1; RC=$?
T1=$(date +%s)
{ echo "host: $(hostname) (local, darwin)"; echo "date_utc: $(date -u +%FT%TZ)"; echo "script_dir_head: 42fe578 (as stated by lead; git not run)"; echo "env: PYTHONHASHSEED=0 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1"; echo "command: $CMD"; echo "wall_s: $((T1-T0))"; echo "exit_code: $RC"; echo "input_parquet_md5: $(md5 -q $PQ)"; echo "longleaf_source_md5: $(grep -o "\"$ENC\": \"[0-9a-f]*\"" $W/q2local/longleaf_md5.txt)"; echo "script_md5:"; md5 $S/round4_ppi_q2_masking.py $S/round4_ppi_estimator.py $S/round3_b1_ppi.py; python -c "import numpy,pandas,scipy,sys;print('python',sys.version.split()[0],'numpy',numpy.__version__,'pandas',pandas.__version__,'scipy',scipy.__version__)"; } > $OUT/PROVENANCE.txt
exit $RC
