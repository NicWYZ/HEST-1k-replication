#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=20
set -u
# Completes item7_check's A4 anchor step. item7_check (Slurm 9039656) ran round3_a4_scores.py with an absolute
# --out-dir, which the script prefixes with the harness ROOT, so its tables landed under
# hest_replication/work/users/.../item7_check/a4/. This job reads that CSV read-only and runs the committed comparator.
UNIT=item7_anchor_rerun
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
B=/work/users/w/e/weiyang/hest_replication/results
COMMIT=0ff3345c33612cf846cac6f425f7ae7c7324bb67
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=b66915a6-d96c-42d1-b0b7-edb7f5bf423f
HJ=$PWD
OUT=$BASE/F3/map/$UNIT
NEW=/work/users/w/e/weiyang/hest_replication/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F3/map/item7_check/a4/a4_scores_by_task__uni_v2__f3anchor.csv
REF=$B/round3/A4_scores/a4_scores_by_task__uni_v2__mainCCRCC.csv
START=$(date -Iseconds)
[ -d "$SNAP" ] || { echo "snapshot missing: $SNAP"; exit 2; }
if [ -e "$OUT" ]; then echo "OUT exists: $OUT, refusing"; exit 3; fi
mkdir -p "$OUT"
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_8450e231133d",
  "frame_id": "$FRAME",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F3.1 item 7: A4 anchor comparison of item7_check's misplaced a4 table against round 3",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
md5sum "$NEW" "$REF" > inputs_md5.txt
$PY -u $SNAP/code/scripts/round10_final_runs_f3_map_anchor.py a4 "$NEW" "$REF" "$OUT" > anchor_a4.log 2>&1; echo $? > rc_anchor
RC=$(cat rc_anchor); ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "map/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round10_final_runs_f3_map_anchor.py a4 on item7_check's a4_scores_by_task (written under ROOT/work/... because of the absolute --out-dir) against round 3's mainCCRCC table" --config '{"stage":"F3","track_dir":"map","unit":"'$UNIT'","commit":"'$COMMIT'"}' --scripts code/scripts/round10_final_runs_f3_map_anchor.py --inputs "$NEW" "$REF"
for g in PROVENANCE.txt _provenance.json *.json *.txt *.log rc_*; do [ -e "$g" ] && cp "$g" "$HJ"/; done
cat anchor_a4.log | tail -20
exit 0
