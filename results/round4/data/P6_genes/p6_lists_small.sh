#SBATCH -J r4data_p6_lists_small
#SBATCH -A rc_htzhu_pi
#SBATCH -p general
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:40:00

set -euo pipefail
WD=$PWD
REPO=/work/users/w/e/weiyang/hest_replication
PY=$REPO/env/miniforge3/envs/hest/bin/python
export PYTHONHASHSEED=0
export R4_SCRIPTS_DIR=$REPO/code/scripts
export R4_COMMIT=71451d7
OUT=$REPO/results/round4/data/P6_genes
TASKS="PRAD,READ,LYMPH_IDC,HCC"
echo "job=$SLURM_JOB_ID partition=$SLURM_JOB_PARTITION node=$(hostname) date=$(date -Is)" | tee $WD/job_facts.txt
echo "pythonhashseed=$PYTHONHASHSEED commit_env=$R4_COMMIT tasks=$TASKS tag=small" >> $WD/job_facts.txt
echo "ref_main=$(cat $REPO/.git/refs/heads/main 2>/dev/null || echo packed_or_unavailable)" >> $WD/job_facts.txt
md5sum $WD/round4_data_p6_genes.py $REPO/code/scripts/round3_d4_sets.py $REPO/code/scripts/round2_r2_gene_check.py $REPO/code/scripts/round3_a0_harness.py >> $WD/job_facts.txt
echo "--- directory stamp already present:" >> $WD/job_facts.txt
cat "$OUT/_provenance.json" >> $WD/job_facts.txt
set +e
$PY $WD/round4_data_p6_genes.py --stage lists --tasks "$TASKS" --tag small --out "$OUT" 2>&1 | tee $WD/p6_small_stdout.txt
rc=${PIPESTATUS[0]}
set -e
echo "exit_code=$rc" >> $WD/job_facts.txt
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,NodeList,Elapsed,Timelimit,ReqCPUS,ReqMem,MaxRSS,State >> $WD/job_facts.txt 2>/dev/null || true
cp "$OUT/p6_gene_summary__small.csv" $WD/ 2>/dev/null || true
cp "$OUT/p6_skipped_folds__small.csv" $WD/ 2>/dev/null || true
cp "$OUT/PROVENANCE__p6_lists_small.txt" $WD/ 2>/dev/null || true
for t in $(echo "$TASKS" | tr ',' ' '); do for k in 50 200 500; do cp "$OUT/genes__${t}__${k}.csv" $WD/ 2>/dev/null || true; ls -l "$OUT/genes__${t}__${k}.parquet" >> $WD/job_facts.txt 2>/dev/null || true; done; done
ls -lh $WD/ 2>/dev/null || true
exit $rc
