# Round 11, track closeout: submits A6 (and B2, the R10 arm of the conformal step). Run on the login node; it only calls
# sbatch. Usage: round11_closeout_submit_a6.sh <commit> <phase> where phase is one of
#   pilot      conformal selftest, the round 3 CCRCC conformal anchor, LUNG_XENIUM R10 donor conformal, the LUNG_XENIUM and CCRCC R10 chains
#   donor      the 13 other donor-level chains (task x arm)
#   center     center-design predictions not yet run (kidney E; brain R10, P, E), then the institution run after them
#   conformal  every other conformal job (task x arm x fitted design, and the center design on kidney and bowel Visium)
# Sizes: R10 from Slurm 9471138 (kidney donor, 26.5 min, 12.7 GB); P from 9503519 (45 min, 16.2 GB); E from 9518165
# (kidney donor, 2 h 22 min for 51 folds, 54.1 GB), so E jobs ask 80 GB; limits about three times the expected runtime.
set -e
C=$1; PH=$2
CL=/work/users/w/e/weiyang/hest_code/round11-closeout
cd $CL && git fetch -q origin && git checkout -q --detach $C
W=$CL/code/scripts/round11_closeout_run.sh
ROOT=/work/users/w/e/weiyang/hest_replication
R10=$ROOT/results/round10/final_runs
CT=/work/users/w/e/weiyang/st_fed_learn/data/tasks
HM=$R10/F1/data_registry/f1_data_hest_match.csv
DMK=$R10/F1/audit_verdicts/donor_map__kidney__Visium.csv
DMB=$R10/F1/audit_verdicts/donor_map__bowel__Visium.csv
DMR=$R10/F1/audit_verdicts/donor_map__brain__Visium.csv
LB=$ROOT/results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet
IB=$ROOT/results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet
CB=$ROOT/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet
R3TD=$ROOT/results/round3/task_defs/CCRCC.json
cd $ROOT/results/round11/closeout/_slurm
N=0
acc() { N=$((N+1)); [ $((N%2)) = 0 ] && echo rc_tengfei_pi || echo rc_htzhu_pi; }
# sub <name> <unit> <cpus> <mem> <minutes> <scripts> <inputs> [--dependency=..] -- <script> <args...>
sub() {
  local n=$1 u=$2 c=$3 m=$4 t=$5 s=$6 in=$7; shift 7; local dep=""
  if [ "${1#--dependency}" != "$1" ]; then dep=$1; shift; fi
  shift
  echo "$u $(sbatch --parsable $dep -J r11c_$n -p general -A $(acc) -c $c --mem=$m -t $t -o a6_%j.out $W $C A6 $u "A6 $u" "$s" "$in" -- "$@")"
}
SC="code/scripts/round11_closeout_conformal.py code/scripts/round3_a0_harness.py code/scripts/round11_closeout_predict.py"
SD="code/scripts/round11_closeout_a6_donor.py code/scripts/round11_closeout_chain.py code/scripts/round11_closeout_predict.py code/scripts/round11_closeout_hest_join.py code/scripts/round10_final_runs_f1_donor_diag.py code/scripts/round10_final_runs_f2_cluster_values.py code/scripts/round10_final_runs_f2_regimeA.py code/scripts/round10_final_runs_estimators.py code/scripts/round3_a0_harness.py"
arm() { case $1 in R10) echo uni_v2:none:r10;; P) echo uni_v2:ring1:ridgecv;; E) echo uni_v2+hoptimus0+virchow2:ring1:r10;; esac; }
# conformal task arguments
cargs() { case $1 in
  CCRCC) echo "--task-json $CT/kidney__Visium.json --donor-map $HM --map-task CCRCC --round3-td $R3TD --genes-from-parquet $CB --designs random,patient,donor --tag CCRCC";;
  INDIANA_KIDNEY) echo "--task-json $CT/kidney__Visium.json --donor-map $HM --map-task INDIANA_KIDNEY --only-mapped --genes-from-parquet $IB --designs random,donor,slide_out --tag INDIANA_KIDNEY";;
  LUNG_XENIUM) echo "--task-json $CT/lung__Xenium.json --donor-map $HM --map-task LUNG_XENIUM --only-mapped --genes-from-parquet $LB --designs random,donor,slide_out --tag LUNG_XENIUM";;
  kidney__Visium) echo "--task-json $CT/kidney__Visium.json --donor-map $DMK --only-mapped --designs random,donor,slide_out";;
  bowel__Visium) echo "--task-json $CT/bowel__Visium.json --donor-map $DMB --only-mapped --designs random,donor,slide_out";;
esac; }
cins() { case $1 in CCRCC) echo "$CT/kidney__Visium.json $HM $R3TD $CB";; INDIANA_KIDNEY) echo "$CT/kidney__Visium.json $HM $IB";;
  LUNG_XENIUM) echo "$CT/lung__Xenium.json $HM $LB";; kidney__Visium) echo "$CT/kidney__Visium.json $DMK";; bowel__Visium) echo "$CT/bowel__Visium.json $DMB";; esac; }
# conformal resources by arm and task size: big = kidney, bowel; small = CCRCC, INDIANA, LUNG
cres() { case "$1:$2" in
  R10:big) echo "4 40G 360";; R10:small) echo "4 32G 240";;
  P:big) echo "8 56G 900";; P:small) echo "8 40G 480";;
  E:big) echo "8 80G 1500";; E:small) echo "8 72G 720";; esac; }
size() { case $1 in kidney__Visium|bowel__Visium) echo big;; *) echo small;; esac; }
conf() { # task arm fitted-design
  local t=$1 a=$2 d=$3; set -- $(cres $a $(size $t))
  sub c${a}${t:0:3}${d:0:3} a6/conformal/${t}__${a}__${d} $1 $2 $3 "$SC" "$(cins $t)" -- round11_closeout_conformal.py run --arm $a $(cargs $t) --fit-designs $d
}
confc() { # task arm: the center design
  local t=$1 a=$2; set -- $(cres $a big)
  local base; base=$(cargs $t | sed 's/--designs [^ ]*/--designs donor/')
  sub c${a}${t:0:3}cen a6/conformal/${t}__${a}__center $1 $2 $3 "$SC" "$(cins $t)" -- round11_closeout_conformal.py run --arm $a $base --unit center --fit-designs donor
}
dres() { case "$1:$2" in
  R10:corpus) echo "4 32G 120";; P:corpus) echo "4 32G 120";; E:corpus) echo "4 32G 120";;
  R10:LUNG_XENIUM|P:LUNG_XENIUM|E:LUNG_XENIUM) echo "4 32G 480";;
  R10:*) echo "4 32G 180";; P:*) echo "8 48G 240";; E:*) echo "8 80G 360";; esac; }
donor() { # task arm
  local t=$1 a=$2 k=$1; case $t in kidney__Visium|bowel__Visium) k=corpus;; esac; set -- $(dres $a $k)
  sub d${a}${t:0:3} a6/donor/${t}__${a} $1 $2 $3 "$SD" "" -- round11_closeout_a6_donor.py $t $a
}
case $PH in
pilot)
  sub cself a6/conformal/selftest_v1 2 8G 30 "$SC" "" -- round11_closeout_conformal.py selftest
  sub canch a6/conformal/anchor_CCRCC_round3 4 32G 240 "$SC" "$R3TD" -- round11_closeout_conformal.py anchor $R3TD uni_v2
  conf LUNG_XENIUM R10 donor
  donor LUNG_XENIUM R10
  donor CCRCC R10
  ;;
donor)
  for a in R10 P E; do for t in kidney__Visium bowel__Visium CCRCC INDIANA_KIDNEY LUNG_XENIUM; do
    case "$t:$a" in LUNG_XENIUM:R10|CCRCC:R10) continue;; esac; donor $t $a; done; done
  ;;
center)
  J=""
  for x in "kidney__Visium E $DMK" "brain__Visium R10 $DMR" "brain__Visium P $DMR" "brain__Visium E $DMR"; do set -- $x
    case $2 in R10) r="4 32G 90";; P) r="8 48G 120";; E) r="8 80G 240";; esac; set -- $1 $2 $3 $r
    line=$(sub p$2${1:0:3}c predict/$1__$2__center $4 $5 $6 "code/scripts/round11_closeout_predict.py code/scripts/round3_a0_harness.py" "$CT/$1.json $3" -- round11_closeout_predict.py $CT/$1.json $3 center . --arm $(arm $2) --only-mapped)
    echo "$line"; J="$J:${line##* }"; done
  sub inst a6/inst/center_v1 2 24G 60 "code/scripts/round10_final_runs_f3_institution.py code/scripts/round4_conf_c3.py code/scripts/round4_conf_sim.py code/scripts/round4_conf_io.py" "$CL/results/round11/closeout/specs/a6_institution.json" --dependency=afterok$J -- round10_final_runs_f3_institution.py run --config $CL/results/round11/closeout/specs/a6_institution.json --out .
  ;;
conformal)
  for a in R10 P E; do
    for t in CCRCC; do for d in random donor; do conf $t $a $d; done; done
    for t in INDIANA_KIDNEY LUNG_XENIUM kidney__Visium bowel__Visium; do for d in random donor slide_out; do
      [ "$t:$a:$d" = "LUNG_XENIUM:R10:donor" ] && continue; conf $t $a $d; done; done
    for t in kidney__Visium bowel__Visium; do confc $t $a; done
  done
  ;;
esac
