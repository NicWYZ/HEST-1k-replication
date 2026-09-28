#SBATCH -J r4data_p6_verify
#SBATCH -A rc_htzhu_pi
#SBATCH -p general
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 00:30:00

set -euo pipefail
WD=$PWD
REPO=/work/users/w/e/weiyang/hest_replication
PY=$REPO/env/miniforge3/envs/hest/bin/python
export PYTHONHASHSEED=0
export R4_SCRIPTS_DIR=$REPO/code/scripts
export R4_COMMIT=71451d7
OUT=$REPO/results/round4/data/P6_genes
echo "job=$SLURM_JOB_ID partition=$SLURM_JOB_PARTITION node=$(hostname) date=$(date -Is)" | tee $WD/job_facts.txt
echo "pythonhashseed=$PYTHONHASHSEED commit_env=$R4_COMMIT" >> $WD/job_facts.txt
echo "ref_main=$(cat $REPO/.git/refs/heads/main 2>/dev/null || echo packed_or_unavailable)" >> $WD/job_facts.txt
md5sum $WD/round4_data_p6_genes.py $REPO/code/scripts/round3_d4_sets.py $REPO/code/scripts/round2_r2_gene_check.py $REPO/code/scripts/round3_a0_harness.py >> $WD/job_facts.txt
set +e
$PY $WD/round4_data_p6_genes.py --stage verify --out "$OUT" 2>&1 | tee $WD/p6_verify_stdout.txt
rc=${PIPESTATUS[0]}
set -e
echo "exit_code=$rc" >> $WD/job_facts.txt
# PROVENANCE.txt is rebuilt here, once, by the last job of the track: one writer, no race.
{ echo "Round 4, stage P, P6 (Genes track) output directory."
  echo "Directory stamp: _provenance.json (longleaf-provenance stamp_dir format)."
  echo "Per-job records follow, one per job that wrote here."
  echo
  cat "$OUT"/PROVENANCE__p6_*.txt
} > "$OUT/PROVENANCE.txt"
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,NodeList,Elapsed,Timelimit,ReqCPUS,ReqMem,MaxRSS,State >> $WD/job_facts.txt 2>/dev/null || true
sacct -u $USER -S 2026-09-28 -X -P -o JobID,JobName,Partition,NodeList,Elapsed,Timelimit,ReqCPUS,ReqMem,MaxRSS,State,Submit,Start > $WD/p6_sacct.csv 2>/dev/null || true
cp "$OUT/p6_gene_summary.csv" "$OUT/p6_acceptance.csv" "$OUT/p6_verify_verdict.json" "$OUT/PROVENANCE.txt" "$OUT/PROVENANCE__p6_verify_all.txt" $WD/ 2>/dev/null || true
wc -l "$OUT"/genes__*.csv >> $WD/job_facts.txt 2>/dev/null || true
ls -lh "$OUT"/ >> $WD/job_facts.txt 2>/dev/null || true
exit $rc
