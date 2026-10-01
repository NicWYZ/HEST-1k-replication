#!/bin/bash
#SBATCH --account=rc_htzhu_pi
#SBATCH -p general
#SBATCH -n 4
#SBATCH --mem=16G
#SBATCH --time=01:30:00
export PYTHONHASHSEED=0
REPO=/work/users/w/e/weiyang/hest_replication
CLONE=/work/users/w/e/weiyang/hest_code/round4-ppi
export PYTHONPATH=$CLONE/code/scripts:$PYTHONPATH
PY=$REPO/env/miniforge3/envs/hest/bin/python
REL=results/round4/ppi/Q0_setup/anchor
WD=$(pwd)
OUT=$REPO/$REL
RUN=$REL/run
cd $WD
T0=$(date +%s)
mkdir -p "$OUT"
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_3a4e23273fb6",
  "frame_id": "42264d40-9a43-4e09-9940-83ba09ea0dae",
  "track": "r4ppi_Q0_anchor",
  "plan": "round4_ppi_plan",
  "note": "B1 anchor rerun CCRCC resnet50",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
mkdir -p $OUT/run
cp $WD/q0_anchor_compare.py $WD/q0_anchor_job.sh $OUT/ 2>/dev/null || true
cd $REPO
HARN_MD5=$(md5sum $CLONE/code/scripts/round3_a0_harness.py | cut -d' ' -f1)
B1_MD5=$(md5sum $CLONE/code/scripts/round3_b1_ppi.py | cut -d' ' -f1)
CMP_MD5=$(md5sum $WD/q0_anchor_compare.py | cut -d' ' -f1)
JOB_MD5=$(md5sum $WD/q0_anchor_job.sh | cut -d' ' -f1)
COMMIT=$(git -C $CLONE rev-parse HEAD)
IMPORT_CHECK=$($PY - <<PYEOF
import os, importlib
clone = "$CLONE"
for m in ("round3_a0_harness", "round3_b1_ppi", "round3_d4_sets"):
    try:
        mod = importlib.import_module(m)
    except ModuleNotFoundError:
        print(m, "NOT_PRESENT_IN_CLONE_AND_NOT_IMPORTED"); continue
    print(m, mod.__file__)
    assert mod.__file__.startswith(clone), (m, mod.__file__)
print("IMPORT_CHECK_OK")
PYEOF
)
echo "$IMPORT_CHECK"
echo "$IMPORT_CHECK" | grep -q IMPORT_CHECK_OK || { echo IMPORT CHECK FAILED; exit 4; }
echo "harness md5 $HARN_MD5 commit $COMMIT partition $SLURM_JOB_PARTITION node $(hostname)"
[ "$HARN_MD5" = "0ad7ae8efe554c1f285e5f384a9fb7f5" ] || { echo "HARNESS MD5 MISMATCH"; exit 3; }
CMD1="$PY $CLONE/code/scripts/round3_b1_ppi.py --predict resnet50 --task-def $REPO/results/round3/task_defs/CCRCC.json --design donor --out-dir $RUN"
CMD2="$PY $CLONE/code/scripts/round3_b1_ppi.py --estimate --out-dir $RUN --b2-dir $REL/b2_unused"
CMD3="$PY $WD/q0_anchor_compare.py $OUT/run/b1_acceptance.csv $REPO/results/round3/B1_ppi/b1_acceptance.csv $OUT/q0_anchor_compare.csv $OUT/q0_anchor_compare_summary.json"
cat > $OUT/config.json <<EOF
{"stage":"r4ppi_Q0_anchor","encoder":"resnet50","task":"CCRCC","design":"donor","variant":"","n_boot":500,"exact_tol":1e-10,"compare_tol":1e-10,"script_args_unmodified":true,"cmd_predict":"round3_b1_ppi.py --predict resnet50 --task-def results/round3/task_defs/CCRCC.json --design donor --out-dir $RUN","cmd_estimate":"round3_b1_ppi.py --estimate --out-dir $RUN"}
EOF
CHASH=$(sha256sum $OUT/config.json | cut -c1-16)
echo "== predict"; date
set +e
$CMD1; RC1=$?
echo "predict rc $RC1"; date
RC2=NA; RC3=NA
if [ $RC1 -eq 0 ]; then
  $CMD2; RC2=$?
  echo "estimate rc $RC2"; date
  if [ -f $OUT/run/b1_acceptance.csv ]; then $CMD3; RC3=$?; echo "compare rc $RC3"; fi
fi
set -e
T1=$(date +%s)
cat > $OUT/PROVENANCE.txt <<EOF
stage           : r4ppi_Q0 / B1 anchor (plan Q0 step 4)
job_prefix      : r4ppi_ (intended; job identified by Slurm id)
slurm_job_id    : $SLURM_JOB_ID
slurm_partition : $SLURM_JOB_PARTITION
node            : $(hostname)
date            : $(date -Iseconds)
repo_commit     : $COMMIT (git -C $CLONE, branch round4-ppi; data root $REPO not used for code)
import_check    : $(echo $IMPORT_CHECK | tr '\n' ' ')
command_predict : $CMD1
command_estimate: $CMD2
command_compare : $CMD3
config_hash     : sha256/16 $CHASH (config.json alongside)
pythonhashseed  : $PYTHONHASHSEED
python          : $($PY --version 2>&1)
md5 round3_b1_ppi.py (run from repo, unmodified) : $B1_MD5
md5 round3_a0_harness.py (expected 0ad7ae8efe554c1f285e5f384a9fb7f5) : $HARN_MD5
md5 q0_anchor_compare.py : $CMP_MD5
md5 q0_anchor_job.sh : $JOB_MD5
rc predict/estimate/compare : $RC1 / $RC2 / $RC3
wall_seconds    : $((T1-T0))
EOF
cp -r $OUT $WD/anchor_out
ls -lh $OUT $OUT/run | head -60
