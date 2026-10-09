INDIANA_KIDNEY, E4b rejective-design unit, round 5 PPI, interval 3.
Frame id stamped: f3629691-72f4-403b-9e99-f5be8a190f85
Snapshot: /work/users/w/e/weiyang/hest_code/round5-ppi_snapshots/9185bc6be157ee9c62d8d1067e5ad9e14f53984e
Ran round5_ppi_e4b_rejective.py via round5_ppi_run.py (--stage E4b) on Longleaf, one job per arm x estimand x n_L:
4 arms (hoptimus0, uni_v2, resnet50, permuted) x theta3, theta2 x n_L 4,6,8,12 = 32 production jobs, defaults --draws 2000 --pool-cand 500,
--ref-arm resnet50, --perm-parquet and --parquet as in E4 (permuted arm uses the resnet50 parquet for --parquet, as E4 did).
Plus 1 pilot (resnet50 theta3 nL8, 5 genes, 100 draws; in _pilot/) and 3 failed jobs (see below). 36 Slurm jobs in all (e4b_job_ledger).
Unusual:
 - The first three permuted theta3 jobs (nL4, 6, 8) failed within 20 s: I passed a nonexistent permuted parquet to --parquet. Resubmitted with the resnet50 parquet (as E4's command); no other effect. The failed jobs are in the ledger (state FAILED).
 - Slurm reports partition 'spill' on every job (submitted with -p general).
 - Skipped: rej_t is skipped on D2 pcF2/pcE2 at n_L=4 (all 8 skipped files are the n_L=4 cells, 4 rows each; no cell was skipped for n_L > G - 2); see e4b_skipped files.
 - Time limit was set generously (8 h); the longest job ran 0 days 00:05:31. Memory 16G; max RSS 1.7 GB.
 - _draws/ stays on Longleaf.
Acceptance summary in e4b_unit_acceptance__INDIANA_KIDNEY.csv. Acceptance 3 and predictions not computed (lead).
