#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=90
set -u
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=b934827e1ad580bc3cf61f43e29d18aa06bccaee
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
PROJ=/work/users/w/e/weiyang/hest_replication
HJ=$PWD
OUT=$BASE/F2/cellvit_download
SETDIR=$BASE/F2/cellvit_seg
LISTING=$PROJ/results/round3/D0_inventory/hf_file_listing.csv.gz
VERD=$BASE/F1/audit_verdicts
REV=7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec
START=$(date -Iseconds)
mkdir -p "$BASE/_snapshots"
exec 9>"$BASE/_snapshots/.lock"; flock 9
if [ ! -d "$SNAP" ]; then
  mkdir -p "$SNAP.tmp" && git -C "$CLONE" archive "$COMMIT" code | tar -x -C "$SNAP.tmp"
  (cd "$SNAP.tmp" && find code -type f -name '*.py' | sort | xargs md5sum > MD5SUMS)
  chmod -R a-w "$SNAP.tmp" && mv "$SNAP.tmp" "$SNAP"
fi
flock -u 9
for d in "$OUT" "$SETDIR"; do if [ -e "$d" ]; then echo "exists: $d, refusing"; exit 3; fi; done
mkdir -p "$OUT" "$SETDIR"
for d in "$OUT" "$SETDIR"; do
cat > "$d/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_8450e231133d",
  "frame_id": "311f766a-9eaf-4808-9fe7-7f16ec282d07",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F2 option (b): HEST-1k CellViT segmentations for corpus samples without one, approved by Nicolas on 10 Nov 2026",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
done
echo "df before:"; df -h /work | tail -1
cd "$OUT"
export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts HF_HOME=/work/users/w/e/weiyang/hf_cache OMP_NUM_THREADS=2
CMD="round10_final_runs_f2_cellvit_download.py $LISTING $VERD $SETDIR $OUT --revision $REV --have-roots $PROJ/hest_ext $PROJ/bench_data"
set +e
$PY -u $SNAP/code/scripts/$CMD > stdout.log 2>&1
RC=$?
set -e
ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC
echo "df after:"; df -h /work | tail -1
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F2 cellvit_download $COMMIT $SNAP "$START" $ST --frame 311f766a-9eaf-4808-9fe7-7f16ec282d07 --command "$CMD" --config '{"stage":"F2","unit":"cellvit_download","commit":"'$COMMIT'","revision":"'$REV'"}' --scripts code/scripts/round10_final_runs_f2_cellvit_download.py --inputs $LISTING $VERD/donor_map__kidney__Visium.csv $VERD/donor_map__brain__Visium.csv $VERD/donor_map__bowel__Visium.csv $VERD/donor_map__breast__Spatial_Transcriptomics.csv $VERD/donor_map__breast__Xenium.csv $VERD/donor_map__lung__Xenium.csv
cp "$OUT/PROVENANCE.txt" "$SETDIR/PROVENANCE.txt"
cd "$OUT"; cp PROVENANCE.txt _provenance.json stdout.log cellvit_download_summary.json cellvit_download_verification.csv "$HJ"/ 2>/dev/null; true
tail -40 stdout.log
exit $RC
