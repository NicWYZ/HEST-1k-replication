#!/bin/bash
G=$1
D=/Users/nicolaszhang/HEST-1k-replication-PPI/code/scripts
OUT=$PWD/theorem_v2/GL$G
mkdir -p $OUT
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 OMP_NUM_THREADS=1
PY=$(which python)
cat > $OUT/_provenance.json <<PE
{"writer":"claude-science","project_id":"proj_3a4e23273fb6","frame_id":"ab674f84-25c3-4e5f-9a25-e0dbd7583e34","track":"ppi","plan":"","note":"Q2 theorem sim v2 (oracle arm), local run","host":"$(hostname)","created_at":"$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"}
PE
{
echo "host: $(hostname) (local, $(uname -sm))"
echo "repo HEAD (read from .git/HEAD ref, no git run): round4-ppi, lead states 42fe578"
for f in round4_ppi_q2_theorem_sim.py round4_ppi_estimator.py round4_ppi_q1_sim.py; do md5sum $D/$f; done
echo "command: $PY $D/round4_ppi_q2_theorem_sim.py --G-L-grid $G --reps 2000 --out-dir $OUT"
echo "env: PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 OMP_NUM_THREADS=1"
$PY -c "import numpy,pandas,sys;print('python',sys.version.split()[0],'numpy',numpy.__version__,'pandas',pandas.__version__)"
} > $OUT/PROVENANCE.txt
/usr/bin/time -l $PY $D/round4_ppi_q2_theorem_sim.py --G-L-grid $G --reps 2000 --out-dir $OUT > $OUT/stdout.txt 2> $OUT/time_l.txt
echo "exit: $?" >> $OUT/PROVENANCE.txt
grep -E "real|maximum resident" $OUT/time_l.txt >> $OUT/PROVENANCE.txt
