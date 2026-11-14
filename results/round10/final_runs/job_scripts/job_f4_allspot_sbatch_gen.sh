#!/bin/bash
# usage: gen.sh <first line> <last line>; builds and submits each remaining all-spot unit from the committed F4 mu check template
set -u
T=/work/users/w/e/weiyang/hest_code/round10-final-runs/results/round10/final_runs/job_scripts/job_f4_mu_check_template.sh
L=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F4/mu_check/_sbatch
mkdir -p $L
sed -n "$1,$2p" /work/users/w/e/weiyang/.claude-science-scratch/tmp/r10fr/f3dec/remaining.tsv | while IFS=$'\t' read -r unit mode arg tl; do
  mkdir -p $L/$unit
  { echo '#!/bin/bash'; echo "#SBATCH --output=$L/$unit/slurm-%j.out"; echo "#SBATCH --chdir=$L/$unit";
    sed -e "s#__UNIT__#$unit#g" -e "s#__MODE__#$mode#g" -e "s#__ARG__#$arg#g" -e "s#__CODE_COMMIT__#d6caff04e0c12e11f8d7bdfcbe53f5f0b5d1ac76#g" -e "s#__MEM__#8G#g" -e "s#__TIME__#$tl#g" $T; } > $L/$unit/job.sbatch
  j=$(sbatch --parsable $L/$unit/job.sbatch) && echo "$unit,$j" >> $L/sbatch_jobs.csv
done
wc -l < $L/sbatch_jobs.csv
