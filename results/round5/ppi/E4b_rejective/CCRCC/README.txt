E4b rejective unit, task CCRCC (round 5 PPI, interval 3). Frame id stamped: bb01cd29-96a1-4687-8166-6a67eeeb8ef8

What ran: round5_ppi_e4b_rejective.py through round5_ppi_run.py (--stage E4b), snapshot
/work/users/w/e/weiyang/hest_code/round5-ppi_snapshots/9185bc6be157ee9c62d8d1067e5ad9e14f53984e, on Longleaf (-p general, -A rc_tengfei_pi,
-c 2, 16G, PYTHONHASHSEED=0). One job per arm (hoptimus0, uni_v2, resnet50, permuted) x estimand (theta3, theta2) x n_L (4, 6, 8, 12) = 32
production jobs, default --draws 2000 and --pool-cand 500; theta2 with the default kind (neo_minus_stroma). Parquets as in E4's PROVENANCE.txt
(the permuted arm reads the resnet50 parquet, as E4 did; --perm-parquet and --ref-parquet are the resnet50 parquet). Pilot: resnet50 theta3 nL8,
--max-genes 5 --draws 100 (35 s, 0.92 GB; output kept on Longleaf under .../CCRCC/_pilot/, not copied). The _draws/ directories stayed on Longleaf.

Layout: <arm>/<estimand>_nL<n>/ holds the driver outputs, PROVENANCE.txt, _run_row.csv, _provenance.json (frame_id checked: 32 of 32 carry the id above).
Unit files: e4b_job_ledger__CCRCC.csv, e4b_unit_acceptance__CCRCC.csv, and detail tables e4b_acc1_rows__CCRCC.csv, e4b_d2_vs_e4_rows__CCRCC.csv,
e4b_d2_diagnostics_all__CCRCC.csv, e4b_skipped_all__CCRCC.csv, e4b_bootstrap_all__CCRCC.csv (inputs for the lead's acceptance 3; not computed here).

Unusual:
 * Three production jobs (permuted theta3 nL4, nL6, nL8; Slurm 4382510, 4382546, 4382578) failed after 7-12 s: my job script pointed the permuted arm at
   b1_predictions__CCRCC__permuted.parquet, which does not exist (E4 used the resnet50 parquet). No outputs were produced. The script was corrected in
   the job command (not in any repository script) and the three cells were resubmitted and completed (4382593, 4383221, 4383224). They are in the ledger.
 * Wall per production job was 2-6 min, so no job timed out and no time limit was raised (limit 4 h).
 * Jobs landed on partition spill (requested general); see ledger.
 * Skipped: no whole cell is skipped (G is 23 or 24, so n_L <= G-2 for every n_L). 32 rej_t rows (all at n_L=4, balances pcF2 and pcE2, D2) are
   skipped because n_L-k-1 < 2; the other intervals in those cells are present.
 * E4 did not write its D2 threshold, so there is no threshold comparison with E4; E4b's thresholds are in e4b_d2_diagnostics.
