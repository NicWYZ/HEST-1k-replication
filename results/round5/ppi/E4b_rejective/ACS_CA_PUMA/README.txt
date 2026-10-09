E4b unit ACS_CA_PUMA (interval 3, stage E4b)
frame_id stamped on every run: 405245f3-badb-4ac9-b9e2-6c231d4e0443
Snapshot: /work/users/w/e/weiyang/hest_code/round5-ppi_snapshots/9185bc6be157ee9c62d8d1067e5ad9e14f53984e (commit 9185bc6be157ee9c62d8d1067e5ad9e14f53984e), script round5_ppi_e4b_rejective.py via round5_ppi_run.py.
Grid: arms package, permuted x estimands theta3, theta2 x n_L 4,6,8,12 = 16 production jobs (one per cell, 2 CPU, 24G, defaults --draws 2000 --pool-cand 500, --theta2-kind mean, 1 gene) + 1 pilot (package theta3 nL8, --max-genes 5 --draws 100; results in _pilot/, not part of the record).
All parquet inputs: results/round4/ppi/Q2_theory/predictions/ACS_CA_PUMA.parquet (as E4: parquet, perm-parquet and ref-parquet are the same file; --ref-arm package).
All 17 jobs COMPLETED on partition spill; no timeouts, no reruns. Per-job wall 1.5-4.8 min; max RSS 1.38 GB.
_draws/ directories stay on Longleaf ($ROOT/results/round5/ppi/E4b_rejective/ACS_CA_PUMA/<arm>/<estimand>_nL<n>/_draws).
No skipped cells (n_L <= 12 <= G-2 = 263; rej_t needs n_L-k-1>=2, satisfied at k=1, n_L=4). No pcE2 cell on ACS. n_beyond_first_batch = 0 in every D2 cell.
D1 balances on ACS: own, pcF, perm, perm_cluster (perm_cluster has no E4 counterpart).
Acceptance tables: e4b_unit_acceptance__ACS_CA_PUMA.csv. E4 did not write its D2 threshold.
Note: the pcF2 D2 rows are identical to own (k=1, one outcome, no embeddings); this is as E4.
