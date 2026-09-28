#!/bin/bash
#SBATCH -J r4data_p0check
#SBATCH -p l40-gpu
#SBATCH --qos=gpu_access
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 00:45:00
#SBATCH -A rc_htzhu_pi
set -euo pipefail
WD=$PWD
REPO=/work/users/w/e/weiyang/hest_replication
PY=$REPO/env/miniforge3/envs/hest/bin/python
export PYTHONHASHSEED=0 HF_HOME=/work/users/w/e/weiyang/hf_cache
mkdir -p $WD/out
echo "partition=$SLURM_JOB_PARTITION node=$(hostname) job=$SLURM_JOB_ID date=$(date -Is)" | tee $WD/out/job_facts.txt
echo "repo_head=$(git -C $REPO rev-parse HEAD)" >> $WD/out/job_facts.txt
md5sum $REPO/code/scripts/round3_d1_download.py $REPO/code/scripts/round3_d2_embed.py >> $WD/out/job_facts.txt
SRC=$REPO/hest_ext/kidney_visium_cell; SID=NCBI692; SET=p0check
X=$WD/ext/$SET
for f in patches/$SID.h5 st/$SID.h5ad cellvit_seg/${SID}_cellvit_seg.parquet cellvit_seg/${SID}_cellvit_seg.geojson.zip metadata/$SID.json; do
  mkdir -p $X/$(dirname $f) $X/.cache/huggingface/download/$(dirname $f)
  ln -s $SRC/$f $X/$f
  cp $SRC/.cache/huggingface/download/$f.metadata $X/.cache/huggingface/download/$f.metadata
done
mkdir -p $WD/emb/$SET/resnet50
ln -s $REPO/embeddings_ext/kidney_visium_cell/resnet50/$SID.h5 $WD/emb/$SET/resnet50/$SID.h5
mkdir -p $WD/d1 $WD/d2
sed "s#__WD__#$WD#g" $WD/d1_config.tmpl.json > $WD/d1/d1_config.json
sed "s#__WD__#$WD#g" $WD/d2_config.tmpl.json > $WD/d2/d2_config.json
echo "=== D1"; (cd $WD/d1 && $PY $REPO/code/scripts/round3_d1_download.py) 2>&1 | tee $WD/out/d1_stdout.txt; echo "d1_rc=${PIPESTATUS[0]}" >> $WD/out/job_facts.txt
echo "=== D2"; (cd $WD/d2 && $PY $REPO/code/scripts/round3_d2_embed.py --set $SET --encoder resnet50 --config d2_config.json) 2>&1 | tee $WD/out/d2_stdout.txt; echo "d2_rc=${PIPESTATUS[0]}" >> $WD/out/job_facts.txt
# the real files must be untouched: links still links, sizes unchanged
for f in patches/$SID.h5 st/$SID.h5ad metadata/$SID.json; do [ -L $X/$f ] && echo "still_link $f" >> $WD/out/job_facts.txt || echo "REPLACED $f" >> $WD/out/job_facts.txt; done
cp $WD/d1/*.csv $WD/d1/PROVENANCE.txt $WD/out/ 2>/dev/null || true
cp $WD/ext/d1_summary.json $WD/out/ 2>/dev/null || true
cp $WD/emb/*.csv $WD/emb/*.json $WD/emb/PROVENANCE__* $WD/out/ 2>/dev/null || true
cp $WD/d1/d1_config.json $WD/out/d1_config_p0.json; cp $WD/d2/d2_config.json $WD/out/d2_config_p0.json
sacct -j $SLURM_JOB_ID --format=JobID,Partition,NodeList,Elapsed,MaxRSS,State >> $WD/out/job_facts.txt || true
mkdir -p "$WD/out"
cat > "$WD/out/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_3a4e23273fb6",
  "frame_id": "dab7c82a-7762-41ec-aaf1-9a41e6afaff2",
  "track": "Setup",
  "plan": "round4 stage P",
  "note": "P0 check: round3 D1 verification and D2 cache check, unchanged scripts, one existing sample (NCBI692)",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
