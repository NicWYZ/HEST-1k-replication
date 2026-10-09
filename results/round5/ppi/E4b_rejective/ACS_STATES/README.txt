E4b, task ACS_STATES (interval 3, round 5 PPI). Frame id stamped: d40a201a-c175-40bc-a9e2-c0c344ddac92
Snapshot: /work/users/w/e/weiyang/hest_code/round5-ppi_snapshots/9185bc6be157ee9c62d8d1067e5ad9e14f53984e
Script: round5_ppi_e4b_rejective.py via round5_ppi_run.py (--stage E4b --unit E4b_ACS_STATES), --theta2-kind mean,
 --ref-arm package, defaults --draws 2000 --pool-cand 500; parquet paths as in E4's PROVENANCE.txt.
Grid: arms package, permuted x estimands theta3, theta2 x n_L 4, 6, 8, 12 = 16 production jobs (one per cell), plus one
 pilot (package, theta3, nL 8, --max-genes 5 --draws 100, under _pilot/). All 17 Slurm jobs COMPLETED, no resubmission.
 Production jobs: 16 GB / 2 cpu / 120 min requested; each ran 1.4-4 min; max RSS 1.68 GB (pilot). _draws/ stays on Longleaf under
 $ROOT/results/round5/ppi/E4b_rejective/ACS_STATES/<arm>/<estimand>_nL<n>/_draws.
Files: <arm>/<estimand>_nL<n>/ (PROVENANCE.txt, _run_row.csv, _provenance.json, e4b_* csv/json), e4b_job_ledger__ACS_STATES.csv,
 e4b_unit_acceptance__ACS_STATES.csv (parts a-d).
Notes: no cell skipped (G = 51; the e4b_skipped files are empty). n_beyond_first_batch = 0 in every D2 cell (max candidates used 1,291).
 Minimum D2 support 2,499. E4 did not write its D2 threshold; the thresholds in the acceptance file are E4b's only.
 On ACS, D2 rows for balance 'own' and 'pcF2' are identical in emp_var_median, coverage_mean and width_median in every cell (checked): True.
 Acceptance 1: 160 of 160 D0/D1 n_sub=200 rows reproduce E4 exactly (max differences 0); perm_cluster has no E4 counterpart (32 rows).
 Acceptance 2: max |rej_t - classical| = 0.0 over 128 D2 cells. Acceptance 3 not computed here (lead merges).
All _provenance.json files (17) carry the id above.
