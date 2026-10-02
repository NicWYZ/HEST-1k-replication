#!/bin/bash
# usage: run_q2.sh ARM PARQUET NL
ARM=$1; PQ=$2; NL=$3
S=/Users/nicolaszhang/HEST-1k-replication-PPI/code/scripts
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
O=$PWD/q2/INDIANA_KIDNEY__${ARM}/nL${NL}
mkdir -p $O
[ -e $O/PROVENANCE.txt ] && { echo "exists $O"; exit 0; }
A=$ARM; PARQ=$PQ
cat > $O/_provenance.json <<J
{"writer":"claude-science","project_id":"proj_3a4e23273fb6","frame_id":"29d26232-3024-422c-8c8b-0dd27509ba09","track":"round4-ppi-Q2","plan":"round4_ppi","note":"Q2 masking Indiana kidney arm=$ARM nL=$NL (local)","host":"$(hostname)","created_at":"$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"}
J
CMD="python $S/round4_ppi_q2_masking.py --parquet $PQ --vtag INDIANA_KIDNEY --arm $ARM --nl-grid $NL --out-dir $O"
{
echo "host: $(hostname) (local, authorised by lead plan 12.2); clone HEAD of scripts dir: 42fe578 (per lead)"
echo "PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1"
md5 $S/round4_ppi_q2_masking.py $S/round4_ppi_estimator.py $S/round3_b1_ppi.py $S/round3_a0_harness.py
echo "input parquet md5 (local): $(md5 -q $PQ)"
python -c "import numpy,pandas,scipy,pyarrow,sys;print(sys.version.split()[0],'numpy',numpy.__version__,'pandas',pandas.__version__,'scipy',scipy.__version__,'pyarrow',pyarrow.__version__)"
echo "cmd: $CMD"
} > $O/PROVENANCE.tmp
START=$(date +%s)
python $PWD/timed.py $CMD > $O/stdout.txt 2> $O/time.txt
rc=$?
END=$(date +%s)
{ cat $O/PROVENANCE.tmp; echo "exit $rc; wall_s $((END-START))"; echo "timed.py md5 $(md5 -q $PWD/timed.py): $(tail -1 $O/time.txt)"; } > $O/PROVENANCE.txt
rm $O/PROVENANCE.tmp
