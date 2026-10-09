E4b rejective-sampling unit: CCRCC_merged (arms hoptimus0, uni_v2, resnet50, permuted; estimands theta3, theta2; n_L 4, 6, 8, 12)
frame_id (stamped on every run, ledger and acceptance row): fbc2a913-66f7-4784-9f96-33695a91e337

What ran: code/scripts/round5_ppi_run.py with round5_ppi_e4b_rejective.py from snapshot
/work/users/w/e/weiyang/hest_code/round5-ppi_snapshots/9185bc6be157ee9c62d8d1067e5ad9e14f53984e on Longleaf
(account rc_tengfei_pi, -c 2, 16G, 6 h wall; PYTHONHASHSEED=0). One job per arm x estimand x n_L: 32 production jobs
at the production defaults (--draws 2000, --pool-cand 500; --ref-arm resnet50, --perm-parquet and --parquet as in
E4's PROVENANCE) plus 1 pilot (resnet50 theta3 nL8, --max-genes 5 --draws 100), kept under _pilot/.
All 33 jobs COMPLETED; total job wall 2.19 h, 2-6 min per production job, max RSS 1.80 GB.
Output files per cell are in <arm>/<estimand>_nL<n>/ (the _draws/ directory stays on Longleaf under
/work/users/w/e/weiyang/hest_replication/results/round5/ppi/E4b_rejective/CCRCC_merged/).

Files: e4b_job_ledger__CCRCC_merged.csv (sacct, one row per job incl. pilot), e4b_unit_acceptance__CCRCC_merged.csv
(acceptance 1, D2 vs E4, threshold medians, acceptance 2, skipped, beyond-first-batch),
e4b_acc1_detail__CCRCC_merged.csv (row-level acceptance 1 comparison).

Unusual:
- Skipped cells are not driven by n_L > G-2 (G = 23 for theta3, 22 for theta2, so none). The driver skipped rej_t for
  balances pcF2 and pcE2 (k = 2) at n_L = 4, both p_a, because n_L-k-1 < 2: 8 cells, 32 rows.
- Jobs landed on the spill partition (the general-partition request was rerouted); no effect on results.
- E4 did not write its D2 threshold, so there is no E4 threshold to compare; E4b's median threshold is reported.
- Acceptance 2 is NaN in the 32 skipped rej_t rows only (max over the rest is exactly 0.0).
- The D2 comparison with E4 at n_sub = 200 differs by design (E4b's calibration pool is 1,000,000 vs E4's 400,000 samples and
  redraw instead of last-candidate fallback); no tolerance applied.
