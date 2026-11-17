# Round 11, track closeout: submits the A5 strength runs, B4 v2 and the CCRCC anchor v2 (run on the login node; it only calls sbatch).
# Memory and time from the kidney R10 anchor (Slurm 9471138: 12.7 GB peak, 26.5 min at 4 cores), arm E scaled by its feature width.
set -e
C=$1
CL=/work/users/w/e/weiyang/hest_code/round11-closeout
cd $CL && git pull -q --ff-only
W=$CL/code/scripts/round11_closeout_run.sh
R10=/work/users/w/e/weiyang/hest_replication/results/round10/final_runs
CT=/work/users/w/e/weiyang/st_fed_learn/data/tasks
HM=$R10/F1/data_registry/f1_data_hest_match.csv
LB=/work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet
RB=$R10/F3/regimeB
cd /work/users/w/e/weiyang/hest_replication/results/round11/closeout/_slurm
S="code/scripts/round3_a0_harness.py"
sub() { # name unit cpus mem time inputs -- args
  local n=$1 u=$2 c=$3 m=$4 t=$5 in=$6; shift 7
  echo "$u $(sbatch --parsable -J r11c_$n -p general -A $ACC -c $c --mem=$m -t $t -o a5_%j.out $W $C A5 $u "strength $u" "$S" "$in" -- round11_closeout_predict.py "$@")"
}
arm() { case $1 in R10) echo uni_v2:none:r10;; H) echo uni_v2:none:ridgecv;; C) echo uni_v2:ring1:r10;; P) echo uni_v2:ring1:ridgecv;; V) echo virchow2:none:r10;; E) echo uni_v2+hoptimus0+virchow2:ring1:r10;; esac; }
res() { case $1 in R10|C|V) echo "4 32G 90";; H) echo "8 32G 240";; P) echo "8 48G 300";; E) echo "8 96G 180";; esac; }
i=0
for A in H C P V E; do ACC=rc_htzhu_pi; [ $((i%2)) = 1 ] && ACC=rc_tengfei_pi; i=$((i+1)); set -- $(res $A)
  sub k$A predict/kidney__Visium__${A}__donor $1 $2 $3 "$CT/kidney__Visium.json $R10/F1/audit_verdicts/donor_map__kidney__Visium.csv" -- $CT/kidney__Visium.json $R10/F1/audit_verdicts/donor_map__kidney__Visium.csv donor . --arm $(arm $A) --only-mapped; done
ACC=rc_tengfei_pi; set -- $(res P)
sub kPc predict/kidney__Visium__P__center $1 $2 $3 "$CT/kidney__Visium.json $R10/F1/audit_verdicts/donor_map__kidney__Visium.csv" -- $CT/kidney__Visium.json $R10/F1/audit_verdicts/donor_map__kidney__Visium.csv center . --arm $(arm P) --only-mapped
for A in R10 H C P V E; do ACC=rc_htzhu_pi; [ $((i%2)) = 1 ] && ACC=rc_tengfei_pi; i=$((i+1)); set -- $(res $A)
  sub b$A predict/bowel__Visium__${A}__donor $1 $2 $3 "$CT/bowel__Visium.json $R10/F1/audit_verdicts/donor_map__bowel__Visium.csv" -- $CT/bowel__Visium.json $R10/F1/audit_verdicts/donor_map__bowel__Visium.csv donor . --arm $(arm $A) --only-mapped; done
for A in R10 H C P V E; do ACC=rc_htzhu_pi; [ $((i%2)) = 1 ] && ACC=rc_tengfei_pi; i=$((i+1)); set -- $(res $A)
  sub l$A predict/LUNG_XENIUM__${A}__donor $1 $2 $3 "$CT/lung__Xenium.json $HM $LB" -- $CT/lung__Xenium.json $HM donor . --arm $(arm $A) --map-task LUNG_XENIUM --only-mapped --tag LUNG_XENIUM --genes-from-parquet $LB; done
ACC=rc_htzhu_pi
echo "b4v2 $(sbatch --parsable -J r11c_b4v2 -p general -A $ACC -c 2 --mem=24G -t 75 -o b4_%j.out $W $C B4 b4/equal_v2 'equal allocation ACS, estimand keys' 'code/scripts/round10_final_runs_f3_regcomp.py code/scripts/round5_ppi_e3_twolevel.py' $RB -- round11_closeout_b4_equal.py $RB)"
SP=$CL/results/round11/closeout/specs/CCRCC__R10.json
echo "a2c $(sbatch --parsable -J r11c_A2ccrcc2 -p general -A $ACC -c 4 --mem=32G -t 180 -o a2c_%j.out $W $C A2 anchor/CCRCC__R10_v2 'anchor R10 CCRCC chain' 'code/scripts/round11_closeout_predict.py code/scripts/round11_closeout_hest_join.py code/scripts/round10_final_runs_f1_donor_diag.py code/scripts/round10_final_runs_f2_cluster_values.py code/scripts/round10_final_runs_f2_regimeA.py code/scripts/round10_final_runs_estimators.py code/scripts/round3_a0_harness.py' "$SP /work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet" -- round11_closeout_chain.py $SP)"
