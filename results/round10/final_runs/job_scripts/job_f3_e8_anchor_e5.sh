#SBATCH --partition=general
#SBATCH --account=rc_htzhu_pi
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=60
set -u
# F3 5d.4 item 4, E8 anchor of the joining step: round5_ppi_e5_joint.py unchanged from the code snapshot of COMMIT,
# run in a scratch tree whose results/round5/ppi/E3_twolevel points to the committed E3 gene rows. The script reads
# round 5's W3 map with `git show <w3_commit>:<path>`; a shim named git on PATH answers that one call from a copy of
# the committed file, md5-checked against round 5's (4ee7bbf2801f54c0ac1fbb7c309eeba9). The output is compared with
# the committed results/round5/ppi/E5_joint/e5_joint_design.csv (md5 ed3ccea64b935a3d1a8fbf6aa4962805) row by row.
UNIT=__UNIT__
CLONE=/work/users/w/e/weiyang/hest_code/round10-final-runs
BASE=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
COMMIT=__CODE_COMMIT__
SNAP=$BASE/_snapshots/$COMMIT
PY=/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python
FRAME=4ca471b7-8d08-41d9-a9df-67fff51f4222
W3C=69baff381a6f7b7abb8a72649d726efdd21b287d
W3P=results/round5/conformal/W3_real/merged/w3_map_by_task.csv
W3MD5=4ee7bbf2801f54c0ac1fbb7c309eeba9
REF=$CLONE/results/round5/ppi/E5_joint/e5_joint_design.csv
REFMD5=ed3ccea64b935a3d1a8fbf6aa4962805
HJ=$PWD
OUT=$BASE/F3/e8/$UNIT
START=$(date -Iseconds)
mkdir -p "$BASE/_snapshots"
exec 9>"$BASE/_snapshots/.lock"; flock 9
if [ ! -d "$SNAP" ]; then
  mkdir -p "$SNAP.tmp" && git -C "$CLONE" archive "$COMMIT" code | tar -x -C "$SNAP.tmp"
  (cd "$SNAP.tmp" && find code -type f -name '*.py' | sort | xargs md5sum > MD5SUMS)
  chmod -R a-w "$SNAP.tmp" && mv "$SNAP.tmp" "$SNAP"
fi
flock -u 9
if [ -e "$OUT" ]; then echo "OUT exists: $OUT, refusing"; exit 3; fi
mkdir -p "$OUT"
cat > "$OUT/_provenance.json" <<PROVEOF
{
  "writer": "claude-science",
  "project_id": "proj_8450e231133d",
  "frame_id": "$FRAME",
  "track": "final-runs",
  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",
  "note": "F3 5d.4 item 4, E8 anchor: round5_ppi_e5_joint.py unchanged from snapshot $COMMIT",
  "host": "$(hostname)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
}
PROVEOF
cd "$OUT"
mkdir -p inputs work/results/round5/ppi/E5_joint shim
cp "$CLONE/$W3P" inputs/w3_map_by_task.csv
cp "$REF" inputs/e5_joint_design_ref.csv
md5sum inputs/w3_map_by_task.csv inputs/e5_joint_design_ref.csv > inputs/MD5
GOTW=$(md5sum inputs/w3_map_by_task.csv | cut -d' ' -f1); GOTR=$(md5sum inputs/e5_joint_design_ref.csv | cut -d' ' -f1)
[ "$GOTW" = "$W3MD5" ] || { echo "w3 map md5 $GOTW != $W3MD5"; echo 4 > rc_inputs; }
[ "$GOTR" = "$REFMD5" ] || { echo "ref md5 $GOTR != $REFMD5"; echo 4 > rc_inputs; }
ln -s "$CLONE/results/round5/ppi/E3_twolevel" work/results/round5/ppi/E3_twolevel
(cd work && ls results/round5/ppi/E3_twolevel/*/*__regb/e3_regb_genes__*.csv.gz | sort | xargs md5sum) > inputs/E3_regb_genes.md5
cat > shim/git <<'SHIMEOF'
#!/bin/bash
# answers only: git show <W3C>:<W3P>
if [ "$1" = "show" ] && [ "$2" = "$E8_W3C:$E8_W3P" ]; then cat "$E8_W3COPY"; echo "shim git show $2" >> "$E8_SHIMLOG"; exit 0; fi
echo "shim git: unsupported call: $*" >&2; echo "unsupported $*" >> "$E8_SHIMLOG"; exit 9
SHIMEOF
chmod +x shim/git
export E8_W3C=$W3C E8_W3P=$W3P E8_W3COPY=$OUT/inputs/w3_map_by_task.csv E8_SHIMLOG=$OUT/shim_calls.log
export PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
set +e
if [ ! -e rc_inputs ]; then
  (cd work && PATH=$OUT/shim:$PATH $PY -u $SNAP/code/scripts/round5_ppi_e5_joint.py --w3-commit $W3C) > e5_joint.log 2>&1; echo $? > rc_e5
  cp work/results/round5/ppi/E5_joint/e5_joint_design.csv e5_joint_design_rerun.csv
  $PY - > compare.log 2>&1 <<'PYEOF'
import json, numpy as np, pandas as pd
ref = pd.read_csv("inputs/e5_joint_design_ref.csv"); new = pd.read_csv("e5_joint_design_rerun.csv")
keys = ["block", "vtag", "arm", "estimand", "m", "n_L", "w3_part", "K"]
num = [c for c in ref.columns if c not in keys and pd.api.types.is_numeric_dtype(ref[c])]
txt = [c for c in ref.columns if c not in keys and c not in num]
for d in (ref, new):
    for k in keys: d[k] = d[k].astype(str)
mg = ref.merge(new, on=keys, how="outer", suffixes=("_ref", "_new"), indicator=True)
both = mg[mg["_merge"] == "both"]
maxabs = {}
for c in num:
    a, b = both[c + "_ref"].to_numpy(float), both[c + "_new"].to_numpy(float)
    nan_mis = int((np.isnan(a) != np.isnan(b)).sum())
    ok = ~np.isnan(a) & ~np.isnan(b)
    maxabs[c] = dict(max_abs_diff=float(np.max(np.abs(a[ok] - b[ok]))) if ok.any() else 0.0, nan_mismatch=nan_mis)
txt_mis = {c: int((both[c + "_ref"].fillna("") .astype(str) != both[c + "_new"].fillna("").astype(str)).sum()) for c in txt}
row = new[(new.block == "inference") & (new.vtag == "CCRCC") & (new.arm == "uni_v2") & (new.estimand == "theta3") & (new.m == "10")]
wr = float(row.width_ratio.iloc[0]) if len(row) == 1 else None
overall = max(v["max_abs_diff"] for v in maxabs.values())
res = dict(rows_ref=len(ref), rows_new=len(new), rows_matched=int(len(both)),
           rows_only_ref=int((mg["_merge"] == "left_only").sum()), rows_only_new=int((mg["_merge"] == "right_only").sum()),
           duplicate_keys_ref=int(ref.duplicated(keys).sum()), numeric_columns=maxabs, text_mismatches=txt_mis,
           max_abs_diff=overall, check_row=dict(key="inference,CCRCC,uni_v2,theta3,m=10", width_ratio=wr,
           expected=0.9920276526390102, equal=(wr == 0.9920276526390102)),
           byte_identical=open("inputs/e5_joint_design_ref.csv", "rb").read() == open("e5_joint_design_rerun.csv", "rb").read())
res["passed"] = bool(res["rows_matched"] == res["rows_ref"] == res["rows_new"] and overall == 0.0 and
                     all(v["nan_mismatch"] == 0 for v in maxabs.values()) and sum(txt_mis.values()) == 0 and res["check_row"]["equal"])
json.dump(res, open("anchor_e5.json", "w"), indent=1)
print(json.dumps(res))
PYEOF
  echo $? > rc_compare
  grep -q '"passed": true' anchor_e5.json || echo 6 > rc_pass
fi
RC=0
for f in rc_*; do [ -e "$f" ] || continue; v=$(cat "$f"); [ "$v" = "0" ] || RC=$v; done
ST=COMPLETED; [ "$RC" = "0" ] || ST=FAILED_rc$RC
$PY $SNAP/code/scripts/round10_final_runs_provenance.py "$OUT" F3 "e8/$UNIT" $COMMIT $SNAP "$START" $ST --frame $FRAME --command "round5_ppi_e5_joint.py --w3-commit $W3C, unchanged from snapshot $COMMIT, in work/ with E3_twolevel linked from the clone and a git shim serving the W3 map copy (md5 $W3MD5); compared with e5_joint_design.csv (md5 $REFMD5) into anchor_e5.json" --config '{"stage":"F3","track_dir":"e8","unit":"'$UNIT'","commit":"'$COMMIT'","w3_commit":"'$W3C'"}' --scripts code/scripts/round5_ppi_e5_joint.py --inputs $OUT/inputs/w3_map_by_task.csv $OUT/inputs/e5_joint_design_ref.csv
cd "$OUT"
for g in PROVENANCE.txt _provenance.json *.json *.log rc_* inputs/MD5; do [ -e "$g" ] && cp "$g" "$HJ"/; done
true
for g in *.log; do [ -e "$g" ] && echo "=== $g" && tail -5 "$g"; done
exit 0
