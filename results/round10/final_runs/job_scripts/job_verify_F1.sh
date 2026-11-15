#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=20
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
HJ=$PWD
cd $CLONE
EXC=.verify-exceptions-round10-final-runs; [ -e $EXC ] || EXC=/dev/null
$PY code/scripts/verify_numeric_claims.py docs/round10/i02/final-runs/round10_final_runs_F1_report.md --exceptions $EXC --tsv "$HJ/verify_F1.tsv" > "$HJ/verify_F1.txt" 2>&1; RC=$?
tail -80 "$HJ/verify_F1.txt"
exit 0
