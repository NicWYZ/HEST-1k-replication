#SBATCH -J r4data_p6_check
#SBATCH -A rc_htzhu_pi
#SBATCH -p general
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 01:00:00

set -euo pipefail
WD=$PWD
REPO=/work/users/w/e/weiyang/hest_replication
PY=$REPO/env/miniforge3/envs/hest/bin/python
export PYTHONHASHSEED=0
export R4_SCRIPTS_DIR=$REPO/code/scripts
export R4_COMMIT=71451d7
OUT=$REPO/results/round4/data/P6_genes
mkdir -p "$OUT"
echo "job=$SLURM_JOB_ID partition=$SLURM_JOB_PARTITION node=$(hostname) date=$(date -Is)" | tee $WD/job_facts.txt
echo "pythonhashseed=$PYTHONHASHSEED commit_env=$R4_COMMIT" >> $WD/job_facts.txt
echo "head_file=$(cat $REPO/.git/HEAD 2>/dev/null || echo unavailable)" >> $WD/job_facts.txt
echo "ref_main=$(cat $REPO/.git/refs/heads/main 2>/dev/null || echo packed_or_unavailable)" >> $WD/job_facts.txt
md5sum $WD/round4_data_p6_genes.py $REPO/code/scripts/round3_d4_sets.py $REPO/code/scripts/round2_r2_gene_check.py $REPO/code/scripts/round3_a0_harness.py >> $WD/job_facts.txt
if [ -f "$OUT/_provenance.json" ]; then echo "--- pre-existing stamp:" >> $WD/job_facts.txt; cat "$OUT/_provenance.json" >> $WD/job_facts.txt; fi
mkdir -p "$OUT"
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_3a4e23273fb6",
  "frame_id": "dab7c82a-7762-41ec-aaf1-9a41e6afaff2",
  "track": "Genes (P6)",
  "plan": "round4 stage P",
  "note": "P6 training-only gene lists for the Visium donor folds: reproduction checks, per-fold lists at 50/200/500, Xenium intersection panels",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
set +e
$PY $WD/round4_data_p6_genes.py --stage check --out "$OUT" 2>&1 | tee $WD/p6_check_stdout.txt
rc=${PIPESTATUS[0]}
set -e
echo "exit_code=$rc" >> $WD/job_facts.txt
du -sh "$OUT"/d4_rerun 2>/dev/null || true
{ echo "Round 4, stage P, P6 output directory (check job $SLURM_JOB_ID)."
  echo "Per-job records: PROVENANCE__p6_<stage>_<tag>.txt in this directory."
  echo "Directory stamp: _provenance.json (longleaf-provenance stamp_dir format)."
  cat "$OUT"/PROVENANCE__p6_*.txt
} > "$OUT/PROVENANCE.txt" 2>/dev/null || true
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,NodeList,Elapsed,Timelimit,ReqCPUS,ReqMem,MaxRSS,State >> $WD/job_facts.txt 2>/dev/null || true
cp "$OUT"/p6_*.csv "$OUT"/p6_*.json "$OUT"/genes__*.csv "$OUT"/PROVENANCE*.txt $WD/ 2>/dev/null || true
ls -lh $WD/ 2>/dev/null || true
exit $rc
