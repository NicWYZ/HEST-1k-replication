#!/bin/bash
# usage: run_one.sh vtag arm nL   (cwd = loc)
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
V=$1; A=$2; N=$3
S=/Users/nicolaszhang/HEST-1k-replication-PPI/code/scripts
W=$(pwd); OUT=$W/out/${V}__${A}/nL${N}
[ -e "$OUT" ] && { echo EXISTS $OUT; exit 3; }
mkdir -p $OUT
cat > $OUT/_provenance.json <<PE
{"writer":"claude-science","project_id":"proj_3a4e23273fb6","frame_id":"e2341968-ca72-46c3-a417-31beb69f6202","track":"ppi-Q2","note":"Q2 ACS masking, local run","host":"$(hostname)","created_at":"$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"}
PE
CMD="python $S/round4_ppi_q2_masking.py --parquet $W/in/$V.parquet --vtag $V --arm $A --theta2-kind mean --nl-grid $N --draws 200 --out-dir $OUT"
{
echo "host: $(hostname) (local sandbox, darwin)"
echo "script source: /Users/nicolaszhang/HEST-1k-replication-PPI/code/scripts, repo HEAD per lead 42fe578"
md5sum $S/round4_ppi_q2_masking.py $S/round4_ppi_q3_regimes.py $S/round4_ppi_estimator.py $S/round3_b1_ppi.py $W/in/$V.parquet
echo "Longleaf md5 of input (recorded in job 031b6dca): see hand-back; ACS_STATES e18604e1e915ff51f2668719e397ab7a, ACS_CA_PUMA c581e8d0a04c989cfebfe6ee888feb90"
echo "PYTHONHASHSEED=0 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1"
echo "command: $CMD"
python -c "import sys,numpy,pandas,scipy;print(sys.version.split()[0],'numpy',numpy.__version__,'pandas',pandas.__version__,'scipy',scipy.__version__)"
} > $OUT/PROVENANCE.txt 2>&1
T0=$(date +%s)
$CMD > $OUT/stdout.txt 2> $OUT/stderr.txt; RC=$?
echo "exit=$RC wall_s=$(( $(date +%s)-T0 ))" >> $OUT/PROVENANCE.txt
exit $RC
